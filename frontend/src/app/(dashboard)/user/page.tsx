'use client'

import { useProfile } from "@/hooks/useProfile";

export default function User() {
  const { user, isLoadingProfile } = useProfile();

  return (  
    <div>
      {isLoadingProfile ? 'Loading' : user?.username}
    </div>
  );
}

