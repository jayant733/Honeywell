export default function AlertDrawer({ alerts }: { alerts: any[] }) {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div className="absolute top-20 right-4 w-80 flex flex-col gap-2 z-50">
      {alerts.map((alert, idx) => (
        <div 
          key={idx} 
          className={`glass-panel p-4 border-l-4 ${
            alert.severity === 'CRITICAL' ? 'border-[var(--color-heating)]' : 'border-[var(--color-safety)]'
          }`}
        >
          <div className="flex justify-between items-start mb-1">
            <span className="font-bold text-xs uppercase text-[var(--color-primary)]">{alert.type}</span>
            <span className="text-[10px] text-[var(--color-secondary)]">{new Date(alert.timestamp).toLocaleTimeString()}</span>
          </div>
          <p className="text-sm text-[var(--color-secondary)]">{alert.message}</p>
        </div>
      ))}
    </div>
  );
}
