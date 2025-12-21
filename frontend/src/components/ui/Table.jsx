import React from 'react';

export const Table = ({ headers, children }) => {
  return (
    <div className="overflow-x-auto border border-slate-200 rounded-xl shadow-sm">
      <table className="w-full text-sm text-left">
        <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
          <tr>
            {headers.map((header, index) => (
              <th key={index} className="px-6 py-3 font-semibold">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-slate-100">
          {children}
        </tbody>
      </table>
    </div>
  );
};
