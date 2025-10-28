interface WideViewProps {
  data: Record<string, string>[];
}

export function WideView({ data }: WideViewProps) {
  if (!data.length) {
    return <p className="text-muted">داده‌ای موجود نیست.</p>;
  }
  const headers = Object.keys(data[0]);
  return (
    <div className="overflow-x-auto rounded-xl border border-surfaceAlt/40">
      <table className="min-w-full text-sm">
        <thead className="bg-surface/70">
          <tr>
            {headers.map((header) => (
              <th key={header} className="px-3 py-2 text-right text-muted">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx} className="odd:bg-surfaceAlt/40">
              {headers.map((header) => (
                <td key={header} className="px-3 py-2">
                  {row[header] ?? ""}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
