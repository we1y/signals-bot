'use client'

import * as React from "react"
import { useQuery } from "@tanstack/react-query"
import { balanceService } from "@/services/balance.service"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/common/card"

export default function Transactions() {
    const { data, isLoading } = useQuery({
        queryKey: ['transactions'],
        queryFn: () => balanceService.transactions()
    })

    if (isLoading) {
        return <div>Загрузка...</div>;
    }

    if (!data || data.length === 0) {
        return <div>Нет транзакций</div>;
    }

  return (
        <div className='flex flex-col space-y-4 h-96 overflow-y-scroll'>
            {data.map((transaction) => (
                <Card key={transaction.id}>
                    <CardHeader>
                        <CardTitle>{transaction.transaction_type}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {transaction.amount}
                    </CardContent>
                    <CardFooter>
                        {transaction.created_at.toLocaleString()}
                    </CardFooter>
                </Card>
            )).reverse()}
        </div>
  )
}
