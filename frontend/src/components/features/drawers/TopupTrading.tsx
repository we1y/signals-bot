'use client'

import * as React from "react"
import { Button } from "@/components/ui/common/button"
import { Input } from "@/components/ui/common/input"
import { Label } from "@/components/ui/common/label"
import { useMutation, useQuery } from "@tanstack/react-query"
import { balanceService } from "@/services/balance.service"

export default function TopupTrading() {
  const [inputValue, setInputValue] = React.useState<number | undefined>()

  const { data } = useQuery({
    queryKey: ['balance'],
    queryFn: () => balanceService.getUserBalance()
  })

  const mutation = useMutation({
    mutationKey: ['tranfer to trading'],
    mutationFn: (amount: number) => balanceService.transferToTrading(amount),
    onError: (error) => console.log(error),
    onSuccess: (data) => console.log(data)
  })

  const tranferToTrading = () => {
    if (inputValue && inputValue > 0) {
      mutation.mutate(inputValue)
    }
  }

  return (
        <div className='m-4'>
            {data?.balance !== undefined && data?.balance > 0 ? (
              <div className='space-y-4'>
                <Label className="text-black">Введите сумму пополения</Label>
                <Input type="number" placeholder="100" onChange={(e) => setInputValue(e.target.value ? parseFloat(e.target.value) : undefined)}/>
                <Button onClick={tranferToTrading}>Пополнить баланс</Button>
              </div>
            ) : (
              <div>К сожалению мы не нашли средств на вашем балансе</div>
            )}  
        </div>
  )
}