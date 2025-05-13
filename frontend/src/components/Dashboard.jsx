import React, {useState, useEffect} from 'react';
import {Line, Bar} from 'react-chartjs-2';
import {Chart, registerables} from 'chart.js';
import './Dashboard.css'; // Create this file for custom styles

// Register Chart.js components
Chart.register(...registerables);

const Dashboard = () => {
  // State for all dashboard data
  const [dashboardData, setDashboardData] = useState({
    heartRate: 0,
    ecg: [],
    position: null,
    imu: {
      accelerometer: {x: 0, y: 0, z: 0},
      gyroscope: {x: 0, y: 0, z: 0},
      magnetometer: {x: 0, y: 0, z: 0},
    },
    lastUpdate: null,
    connectionStatus: 'disconnected',
    error: null,
  });

  // Helper function to safely access sensor values (removed as unused)

  // Process incoming sensor data
  const processSensorData = (topic, msg) => {
    try {
      setDashboardData((prev) => {
        const newData = {...prev}; // Create a shallow copy of the previous state
        newData.lastUpdate = new Date(); // Update the timestamp
        newData.error = null; // Clear any previous errors
        //console.log(`Processing data from topic: ${topic}`, msg);
        msg = JSON.parse(msg);

        switch (topic) {
          case 'sensors/hr':
            // Ensure msg is parsed and contains the expected structure
            if (typeof msg === 'object' && msg?.average) {
              newData.heartRate = msg.average; // Use the average value if available
            } else if (typeof msg === 'number') {
              newData.heartRate = msg; // Use the number directly if it's a valid HR value
            } else {
              console.warn('Invalid HR data received:', msg);
            }
            break;

          case 'sensors/ecg':
            try {
              // Parse the msg string into a JSON object

              // Check if Samples exists and is an array
              if (msg?.Samples && Array.isArray(msg.Samples)) {
                newData.ecg = msg.Samples.slice(0, 200); // Keep the first 200 samples
              }
            } catch (error) {
              console.error('Failed to parse ECG message:', msg, error);
            }
            break;

          case 'sensors/gnss':
            if (msg?.Latitude && msg?.Longitude) {
              newData.position = {
                lat: parseFloat(msg.Latitude), // Convert Latitude to a float
                long: parseFloat(msg.Longitude), // Convert Longitude to a floa
                timestamp: msg.TimestampUTC || new Date().toISOString(),
              };
            }
            break;

          case 'sensors/imu':
            try {
              // Parse the msg string into a JSON object

              // Process accelerometer
              if (msg?.ArrayAcc) {
                console.log(
                  'X value:' + msg.ArrayAcc[0].x,
                  'type:' + typeof msg.ArrayAcc[0].x
                );

                newData.imu.accelerometer = {
                  x: msg.ArrayAcc[0].x,
                  y: msg.ArrayAcc[0].y,
                  z: msg.ArrayAcc[0].z,
                };
                console.log(
                  'newData.imu.accelerometer' + newData.imu.accelerometer.x
                );
              }

              // Process gyroscope
              if (msg?.ArrayGyro && Array.isArray(msg.ArrayGyro)) {
                newData.imu.gyroscope = {
                  x: msg.ArrayGyro[0].x,
                  y: msg.ArrayGyro[0].y,
                  z: msg.ArrayGyro[0].z,
                };
              }

              // Process magnetometer
              if (msg?.ArrayMagn && Array.isArray(msg.ArrayMagn)) {
                newData.imu.magnetometer = {
                  x: msg.ArrayMagn[0].x,
                  y: msg.ArrayMagn[0].y,
                  z: msg.ArrayMagn[0].z,
                };
              }
            } catch (error) {
              console.error('Failed to parse IMU message:', msg, error);
            }
            break;

          default:
            console.warn(`Received data from unknown topic: ${topic}`);
        }

        return newData;
      });
    } catch (error) {
      setDashboardData((prev) => ({
        ...prev,
        error: `Error processing ${topic}: ${error.message}`,
      }));
      console.error('Data processing error:', error);
    }
  };

  // Connect to SSE stream
  useEffect(() => {
    const eventSourceUrl = 'http://localhost:3001/events';
    const source = new EventSource(eventSourceUrl);

    console.log(`Connecting to SSE at ${eventSourceUrl}`);

    source.onopen = () => {
      console.log('SSE connection established');
      setDashboardData((prev) => ({
        ...prev,
        connectionStatus: 'connected',
        error: null,
      }));
    };

    source.onerror = (e) => {
      console.error('SSE connection error:', e);
      setDashboardData((prev) => ({
        ...prev,
        connectionStatus: 'error',
        error: 'Connection lost. Attempting to reconnect...',
      }));
    };

    source.onmessage = (e) => {
      try {
        const {topic, msg} = JSON.parse(e.data);
        processSensorData(topic, msg);
      } catch (err) {
        console.error('Error parsing SSE message:', err);
      }
    };

    return () => {
      source.close();
      console.log('SSE connection closed');
    };
  }, []);

  // Chart configurations
  const ecgChartData = {
    labels: dashboardData.ecg.map((_, i) => i),
    datasets: [
      {
        label: 'ECG Signal (mV)',
        data: dashboardData.ecg,
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1,
        tension: 0.1,
        pointRadius: 0,
      },
    ],
  };

  const imuChartData = {
    labels: ['X-axis', 'Y-axis', 'Z-axis'],
    datasets: [
      {
        label: 'Accelerometer (m/s²)',
        data: [
          dashboardData.imu.accelerometer.x,
          dashboardData.imu.accelerometer.y,
          dashboardData.imu.accelerometer.z,
        ],
        backgroundColor: 'rgba(54, 162, 235, 0.7)',
      },
      {
        label: 'Gyroscope (rad/s)',
        data: [
          dashboardData.imu.gyroscope.x,
          dashboardData.imu.gyroscope.y,
          dashboardData.imu.gyroscope.z,
        ],
        backgroundColor: 'rgba(255, 206, 86, 0.7)',
      },
      {
        label: 'Magnetometer (µT)',
        data: [
          dashboardData.imu.magnetometer.x,
          dashboardData.imu.magnetometer.y,
          dashboardData.imu.magnetometer.z,
        ],
        backgroundColor: 'rgba(75, 192, 192, 0.7)',
      },
    ],
  };

  // Format last update time
  const formatLastUpdate = () => {
    if (!dashboardData.lastUpdate) return 'Never';
    return dashboardData.lastUpdate.toLocaleTimeString();
  };

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <h1>SPORTS IoT DASHBOARD</h1>
        <div className="status-indicator">
          <span
            className={`connection-status ${dashboardData.connectionStatus}`}
          >
            {dashboardData.connectionStatus.toUpperCase()}
          </span>
          <span className="last-update">Last update: {formatLastUpdate()}</span>
        </div>
      </header>

      {/* Error display */}
      {dashboardData.error && (
        <div className="error-alert">{dashboardData.error}</div>
      )}

      {/* Main dashboard grid */}
      <div className="dashboard-grid">
        {/* Heart Rate Widget */}
        <div className="dashboard-card heart-rate">
          <h2>Heart Rate</h2>
          <div className="heart-rate-value">
            {dashboardData.heartRate} <span className="unit">bpm</span>
          </div>
          <div className="heart-rate-progress">
            <div
              className="progress-bar"
              style={{
                width: `${Math.min(dashboardData.heartRate / 2, 100)}%`,
                backgroundColor:
                  dashboardData.heartRate > 100 ? '#ff4757' : '#2ed573',
              }}
            ></div>
          </div>
        </div>

        {/* Position Widget */}
        <div className="dashboard-card position">
          <h2>GPS Position</h2>
          {dashboardData.position ? (
            <>
              <div className="position-coordinates">
                <div>
                  <span className="label">Latitude:</span>
                  <span className="value">
                    {dashboardData.position.lat.toFixed(6)}
                  </span>
                </div>
                <div>
                  <span className="label">Longitude:</span>
                  <span className="value">
                    {dashboardData.position.long.toFixed(6)}
                  </span>
                </div>
              </div>
              <div className="map-placeholder">
                [Map Visualization Would Appear Here]
                <div className="map-coordinates">
                  {dashboardData.position.lat.toFixed(4)},{' '}
                  {dashboardData.position.long.toFixed(4)}
                </div>
              </div>
            </>
          ) : (
            <div className="no-data">No position data available</div>
          )}
        </div>

        {/* Motion Sensors Widget */}
        <div className="dashboard-card motion-sensors">
          <h2>Motion Sensors</h2>
          <div className="chart-container">
            <Bar
              data={imuChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  y: {
                    beginAtZero: false,
                    title: {
                      display: true,
                      text: 'Sensor Values',
                    },
                  },
                },
                plugins: {
                  legend: {
                    position: 'top',
                  },
                },
              }}
            />
          </div>
        </div>

        {/* ECG Widget */}
        <div className="dashboard-card ecg">
          <h2>ECG Signal</h2>
          {dashboardData.ecg.length > 0 ? (
            <div className="chart-container">
              <Line
                data={ecgChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: false,
                      title: {
                        display: true,
                        text: 'Voltage (mV)',
                      },
                    },
                    x: {
                      title: {
                        display: true,
                        text: 'Samples',
                      },
                    },
                  },
                }}
              />
            </div>
          ) : (
            <div className="no-data">Waiting for ECG data...</div>
          )}
        </div>

        {/* Raw Data Widget (for debugging) */}
        <div className="dashboard-card raw-data">
          <h2>Raw Data Preview</h2>
          <pre>
            {JSON.stringify(
              {
                heartRate: dashboardData.heartRate,
                ecgSamples: dashboardData.ecg.length,
                position: dashboardData.position,
                imu: dashboardData.imu,
              },
              null,
              2
            )}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
