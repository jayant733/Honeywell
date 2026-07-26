import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const data = [
  {
    name: '00:00',
    Baseline: 4000,
    AI: 2400,
  },
  {
    name: '04:00',
    Baseline: 3000,
    AI: 1398,
  },
  {
    name: '08:00',
    Baseline: 2000,
    AI: 4800, // Pre-cooling before occupancy
  },
  {
    name: '12:00',
    Baseline: 8780,
    AI: 3908, // Coasting during peak demand
  },
  {
    name: '16:00',
    Baseline: 9890,
    AI: 4800,
  },
  {
    name: '20:00',
    Baseline: 4390,
    AI: 3800,
  },
];

export default function SavingsChart() {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={data}
        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
        <XAxis dataKey="name" stroke="var(--color-secondary)" />
        <YAxis stroke="var(--color-secondary)" />
        <Tooltip 
          contentStyle={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)', borderRadius: '8px' }}
          itemStyle={{ color: 'var(--color-primary)' }}
        />
        <Legend />
        <Bar dataKey="Baseline" fill="var(--color-secondary)" opacity={0.5} />
        <Bar dataKey="AI" fill="var(--color-success)" />
      </BarChart>
    </ResponsiveContainer>
  );
}
