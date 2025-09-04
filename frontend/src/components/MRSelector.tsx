'use client'

import { useMRList } from '@/hooks/useRouteData'

interface MRSelectorProps {
  selectedMR: number | null
  onSelectMR: (mrId: number | null) => void
}

export function MRSelector({ selectedMR, onSelectMR }: MRSelectorProps) {
  const { mrs, loading } = useMRList()

  return (
    <select
      value={selectedMR || ''}
      onChange={(e) => onSelectMR(e.target.value ? Number(e.target.value) : null)}
      className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
      disabled={loading}
    >
      <option value="">Select MR</option>
      {mrs.map((mr) => (
        <option key={mr.id} value={mr.id}>
          {mr.name}
        </option>
      ))}
    </select>
  )
}
