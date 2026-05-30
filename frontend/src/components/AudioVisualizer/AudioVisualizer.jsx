import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from 'recharts'

const COLORS = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc949']

function asArray(data) {
  if (!data) return []
  if (Array.isArray(data)) return data
  return Object.keys(data).map(k => ({ name: k, value: data[k] }))
}

export default function AudioVisualizer({ type='bar', data }) {
  const arr = asArray(data)
  if (arr.length === 0) return <div className="text-sm text-gray-500">No data</div>

  if (type === 'pie') {
    return (
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie data={arr} dataKey="value" nameKey="name" outerRadius={100} fill="#8884d8">
            {arr.map((entry, idx) => (<Cell key={`c-${idx}`} fill={COLORS[idx % COLORS.length]} />))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    )
  }

  if (type === 'line') {
    return (
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={arr} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid stroke="#1f2937" strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="overall" stroke="#f59e0b" strokeWidth={2} />
          <Line type="monotone" dataKey="silhouette" stroke="#34d399" strokeWidth={1.5} />
          <Line type="monotone" dataKey="calinski" stroke="#22d3ee" strokeWidth={1.5} />
          <Line type="monotone" dataKey="davies" stroke="#f87171" strokeWidth={1.5} />
          <Line type="monotone" dataKey="elapsed" stroke="#d946ef" strokeWidth={1.5} />
          <Line type="monotone" dataKey="memory" stroke="#fbbf24" strokeWidth={1.5} />
        </LineChart>
      </ResponsiveContainer>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={arr} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
        <CartesianGrid stroke="#f5f5f5" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="value" fill="#4e79a7" />
      </BarChart>
    </ResponsiveContainer>
  )
}
