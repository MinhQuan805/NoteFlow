'use client'

import ClientLayout from '@/components/client/ClientLayout'
import StoreProvider from '@/app/(client)/notebook/StoreProvider'

export default function ClientRootLayout({ children }: { children: React.ReactNode }) {
  return (
    <StoreProvider>
        <ClientLayout>
          {children}
        </ClientLayout>
    </StoreProvider>
  )
}
