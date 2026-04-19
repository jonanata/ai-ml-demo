import { useState } from 'react'
import axios from 'axios'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
import { Bar } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend)

export default function Home() {
  const [selectedDate, setSelectedDate] = useState('24-09-2025')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setData(null)
    try {
      const resp = await axios.post('http://localhost:8000/api/predict_risk', { selected_date: selectedDate })
      setData(resp.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const chartData = () => {
    if (!data) return {}
    const labels = data.map(r => r.date)
    const risks = data.map(r => r.accident_risk)
    const temps = data.map(r => r.avg_temperature)
    return {
      labels,
      datasets: [
        {
          type: 'bar',
          label: 'Accident Risk',
          data: risks,
          backgroundColor: risks.map(r => r ? 'rgba(255,99,132,0.6)' : 'rgba(75,192,192,0.6)')
        },
        {
          type: 'line',
          label: 'Avg Temp (°C)',
          data: temps,
          borderColor: 'rgba(54,162,235,1)',
          backgroundColor: 'rgba(54,162,235,0.2)',
          yAxisID: 'y1'
        }
      ]
    }
  }

  const options = {
    scales: {
      y: { beginAtZero: true },
      y1: { position: 'right' }
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Traffic Accident Risk Checker</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: 20 }}>
        <label>
          Selected date (dd-mm-yyyy):
          <input value={selectedDate} onChange={e => setSelectedDate(e.target.value)} style={{ marginLeft: 8 }} />
        </label>
        <button type="submit" style={{ marginLeft: 12 }}>Check Now</button>
      </form>

      {loading && <div>Loading...</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}

      {data && (
        <div>
          <h2>Results</h2>
          <Bar data={chartData()} options={options} />
        </div>
      )}
    </div>
  )
}
