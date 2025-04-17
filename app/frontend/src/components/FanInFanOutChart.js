import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend, ResponsiveContainer } from 'recharts';

export default function FanInFanOutChart({ data }) {
  return (
    <div className="p-4 rounded-xl bg-white shadow-md">
      <h2 className="text-xl font-semibold mb-4">Fan-In / Fan-Out Per Function</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="function" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="fanIn" fill="#82ca9d" name="Fan-In" />
          <Bar dataKey="fanOut" fill="#8884d8" name="Fan-Out" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
