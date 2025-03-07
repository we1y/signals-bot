'use client'

import Balance from "@/components/features/Balance";
import Navigation from "@/components/features/Navigation";
import Signals from "@/components/features/Signals";
import Work from "@/components/features/Work";

export default function Home() {

  return (
    <div className='space-y-2 p-2'>

        <Navigation />
        <Balance />
        <Work />
        <Signals />
    </div>
  );
}

