'use client'

import { Bell, Settings, User } from "lucide-react";
import Link from "next/link";
import { Card } from "@/components/ui/common/card";

export default function Navigation() {
  return (
    <Card>
    <header className="flex h-16 w-full items-center">
      <div className="mx-auto max-w-7xl flex w-full items-center px-4 md:px-6">
        <Link href="#" className="mr-6 flex items-center rounded-3xl py-2 px-2 [&_svg]:size-9" prefetch={false}>
          <User className="bg-background text-primary-foreground rounded-full p-2"/>
          <span className="sr-only">Profile</span>
        </Link>
        <div className="ml-auto flex items-center space-x-4">
        <Link
            href="/notifications"
            className="inline-flex h-9 items-center justify-center py-2 text-sm font-medium transition-colors [&_svg]:size-9"
            prefetch={false}
          >
            <Bell className="bg-background text-primary-foreground rounded-full p-2"/>
          </Link>
          <Link
            href="/settings"
            className="inline-flex h-9 items-center justify-center py-2 text-sm font-medium transition-colors [&_svg]:size-9"
            prefetch={false}
          >
            <Settings className="bg-background text-primary-foreground rounded-full p-2"/>
          </Link>
        </div>
      </div>
    </header>
    </Card>
  );
}

