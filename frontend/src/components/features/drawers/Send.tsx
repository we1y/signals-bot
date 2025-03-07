'use client'

import { Button } from "@/components/ui/common/button"
import { Input } from "@/components/ui/common/input"
import { Label } from "@/components/ui/common/label"
import { useMutation } from "@tanstack/react-query"
import { balanceService } from "@/services/balance.service"
import { useState } from "react"

export default function Send() {
  const [inputValue, setInputValue] = useState<number | undefined>();

  const mutation = useMutation({
      mutationKey: ['tranfer to trading'],
      mutationFn: (amount: number) => balanceService.transferToMain(amount),
      onError: (error) => console.log(error),
      onSuccess: (data) => console.log(data)
    })
  
    const tranferToMain = () => {
      if (inputValue && inputValue > 0) {
        mutation.mutate(inputValue)
      }
    }

  return (
        <div className='space-y-4 m-4'>
            <div>
              <Label className="text-black">Введите сумму перевода</Label>
              <Input type="number" placeholder="100" onChange={(e) => setInputValue(e.target.value ? parseFloat(e.target.value) : undefined)}/>
            </div>
            <Button onClick={tranferToMain}>Перевести</Button>
        </div>
  )
}