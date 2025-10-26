// app/layout.tsx
'use client';

import { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import Link from 'next/link';

export default function RootLayout({ children }: { children: React.ReactNode }) {

  return (
    <div>
      <main>{children}</main>
    </div>
  );
}