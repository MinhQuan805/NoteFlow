// AddSource.tsx

'use client'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/shadcn-io/spinner'
import { Plus } from 'lucide-react'

interface AddSourceProps {
  onAdd: (e: React.ChangeEvent<HTMLInputElement>) => void
  loading: boolean
}

export default function AddSource({ onAdd, loading }: AddSourceProps) {
  return (
    <label className="w-full h-10 flex font-semibold justify-center items-center gap-1 px-3 py-1.5 
                      text-sm rounded-3xl cursor-pointer border border-gray-300 hover:bg-gray-100">
      <Input type="file" className="hidden" multiple onChange={onAdd} />
      {loading ? (
        <Spinner variant="ring" className="w-4 h-4" />
      ) : (
        <>
          <Plus size={16} /> Add
        </>
      )}
    </label>
  )
}
