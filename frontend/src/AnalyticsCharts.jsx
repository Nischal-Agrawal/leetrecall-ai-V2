import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

export function DecayChart({ data }) {
  return (
    <div className="recharts-scroll" style={{ height: Math.max(300, data.length * 34) }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 8, right: 24, left: 20, bottom: 8 }}>
          <CartesianGrid stroke="rgba(148,163,184,0.12)" horizontal={false} />
          <XAxis type="number" domain={[0, 100]} unit="%" stroke="#94a3b8" />
          <YAxis type="category" dataKey="label" width={190} tick={{ fill: '#cbd5e1', fontSize: 12 }} />
          <Tooltip formatter={(value) => [`${value}%`, 'Forget probability']} />
          <Bar dataKey="value" name="Forget probability" fill="#fb7185" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function TopicCoverageChart({ data, labelKey, valueKey, title }) {
  return (
    <div className="recharts-scroll" style={{ height: Math.max(320, data.length * 34) }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 8, right: 24, left: 20, bottom: 8 }}>
          <CartesianGrid stroke="rgba(148,163,184,0.12)" horizontal={false} />
          <XAxis type="number" domain={[0, 100]} unit="%" stroke="#94a3b8" />
          <YAxis type="category" dataKey={labelKey} width={170} tick={{ fill: '#cbd5e1', fontSize: 12 }} />
          <Tooltip formatter={(value) => [`${value}%`, title]} />
          <Bar dataKey={valueKey} name={title} fill="#34d399" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}