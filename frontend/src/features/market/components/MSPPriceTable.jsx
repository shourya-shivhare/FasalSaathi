import React from 'react';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';

const MSPPriceTable = ({ mspData }) => {
  const getChangeBadgeVariant = (change) => {
    if (change > 0) return 'success';
    if (change < 0) return 'danger';
    return 'neutral';
  };

  const formatChange = (change) => {
    const sign = change > 0 ? '+' : '';
    return `${sign}${change}%`;
  };

  return (
    <Card>
      <h3 className="text-lg font-semibold text-stone-900 mb-4">Government MSP Rates</h3>
      
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-stone-200">
              <th className="text-left py-3 px-2 font-medium text-stone-700">Crop</th>
              <th className="text-right py-3 px-2 font-medium text-stone-700">MSP 2024-25</th>
              <th className="text-right py-3 px-2 font-medium text-stone-700">MSP 2023-24</th>
              <th className="text-right py-3 px-2 font-medium text-stone-700">Change</th>
            </tr>
          </thead>
          <tbody>
            {mspData.map((item, index) => (
              <tr 
                key={item.crop}
                className={`border-b border-stone-100 ${
                  index % 2 === 0 ? 'bg-white' : 'bg-stone-50'
                }`}
              >
                <td className="py-3 px-2 font-medium text-stone-900">
                  {item.crop}
                </td>
                <td className="text-right py-3 px-2 text-stone-900">
                  ₹{item.msp2024}
                </td>
                <td className="text-right py-3 px-2 text-stone-600">
                  ₹{item.msp2023}
                </td>
                <td className="text-right py-3 px-2">
                  <Badge variant={getChangeBadgeVariant(item.change)}>
                    {formatChange(item.change)}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <div className="text-xs text-blue-800">
          <p className="font-medium mb-1">Note:</p>
          <ul className="space-y-1">
            <li>• MSP rates are per quintal unless specified</li>
            <li>• Rates are for common varieties of each crop</li>
            <li>• Sugarcane rates are per tonne</li>
          </ul>
        </div>
      </div>
    </Card>
  );
};

export { MSPPriceTable };
