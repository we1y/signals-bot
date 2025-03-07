'use client'

import BackButton from "@/components/features/telegram/BackButton"
import { Button } from "@/components/ui/common/button"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/common/card"
import { Input } from "@/components/ui/common/input"
import { signalService } from "@/services/signal.service"
import { userService } from "@/services/user.service"
import { JoinSignal } from "@/types/signal.interface"
import { useMutation, useQuery } from "@tanstack/react-query"
import { useState } from "react"

export default function Signals() {
    const [inputValue, setInputValue] = useState<number | undefined>();

    const { data, isLoading } = useQuery({
        queryKey: ['active signals'],
        queryFn: () => signalService.activeSignals() 
    })

    const user = useQuery({
        queryKey: ['user telegram id'],
        queryFn: () => userService.getUser()
    })

    const mutation = useMutation<unknown, JoinSignal, JoinSignal>({
        mutationKey: ['join signal'],
        mutationFn: ({ telegram_id, signal_id, amount }) => signalService.joinSignal(telegram_id, signal_id, amount),
        onSuccess: (data) => console.log(data),
        onError: (error) => console.log(error)
    })

    if (isLoading) return <div>Loading</div>

    if (!data?.active_signals) return <div>No active signals available</div>

    return (
        <div className='flex flex-col m-6 space-y-4 overflow-y-scroll'>
        <BackButton />
        {data?.active_signals?.map((signal) => (
            <Card key={signal.signal_id}>
                <CardHeader className="font-bold">
                    {signal.name}
                </CardHeader>
                <CardContent className='flex-col'>
                    {/* <p>Signal_id: {signal.signal_id}</p>
                    <p>Join_until: {signal.join_until.toString()}</p>
                    <p>Expires_in: {signal.expires_at.toString()}</p> */}
                    <Input type="number" placeholder="Введите сумму для входа в сигнал" onChange={(e) => setInputValue(e.target.value ? parseFloat(e.target.value) : undefined)}/>
                </CardContent>
                <CardFooter>
                    <Button onClick={() => mutation.mutate({
                        telegram_id: user.data?.telegram_id ?? 0,
                        signal_id: signal.signal_id,
                        amount: inputValue ?? 0
                    })}>Войти</Button>
                </CardFooter>
            </Card>
        ))}
        </div>
    )
}