'use client'

import * as React from "react";
import {
  Card,
  CardDescription,
  CardTitle,
} from "@/components/ui/common/card"
import { ArrowRight, Clock } from "lucide-react"
import Link from "next/link"
import { useQuery } from "@tanstack/react-query";
import { signalService } from "@/services/signal.service";

export default function Signals() {
    const { data, isLoading } = useQuery({
        queryKey: ['signals'],
        queryFn: () => signalService.activeSignals()
    })

    return (
            <Card className='flex items-center justify-between p-4'>
                <Clock />
                <div>
                    <CardTitle>В РАБОТЕ</CardTitle>
                    <CardDescription className="text-muted">
                        {isLoading ? 'Загрузка...' : data?.active_signals[0]?.name}
                    </CardDescription>
                </div>
                <Link href='/signals' className="[&_svg]:size-9">
                    <ArrowRight className='cursor-pointer bg-background text-primary-foreground rounded-full p-2' />
                </Link>
            </Card>
    )
}