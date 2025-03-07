'use client'

import * as React from "react"
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/common/card"
import { useQuery } from "@tanstack/react-query"
import { balanceService } from "@/services/balance.service"
import { VisuallyHidden } from "@radix-ui/react-visually-hidden"
import { Button } from "@/components/ui/common/button"
import { Drawer, DrawerTrigger, DrawerContent, DrawerTitle } from "@/components/ui/common/drawer"
import TopupTrading from "@/components/features/drawers/TopupTrading"

export default function Balance() {
  const { data, isLoading } = useQuery({
		queryKey: ['balance'],
		queryFn: () => balanceService.getUserBalance()
	})

  return (
        <Card className='text-center'>
            <CardHeader>
                <CardTitle>
                  ТОРОГОВЫЙ БАЛАНС
                </CardTitle>
            </CardHeader>
            <CardContent className="font-bold text-2xl">
                {isLoading ? 'Загрузка...' : data?.trade_balance.toFixed(5)} USDT
            </CardContent>
            <CardFooter className="pb-2 px-2">
                  <Drawer>
                        <DrawerTrigger asChild>
                            <Button className='h-full w-full flex flex-col rounded-xl items-center font-black text-sm'>
                                Пополнить торговый баланс с баланса
                            </Button>
                        </DrawerTrigger>
                        <DrawerContent aria-describedby={undefined} className='flex items-center'>
                            <DrawerTitle>
                                <VisuallyHidden>Пополнить</VisuallyHidden>
                            </DrawerTitle>
                                <TopupTrading />
                        </DrawerContent>
                    </Drawer>    
            </CardFooter>
        </Card>
  )
}
