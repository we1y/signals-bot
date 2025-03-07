'use client'

import * as React from "react"
import {
  Card,
  CardContent,
  CardFooter,
} from "@/components/ui/common/card"
import { Label } from "@/components/ui/common/label"
import { MoveDown, Plus, Text, Users } from "lucide-react"
import { Drawer, DrawerTrigger, DrawerContent, DrawerTitle } from "@/components/ui/common/drawer"
import { Button } from "@/components/ui/common/button"
import Send from "@/components/features/drawers/Send"
import Referrals from "@/components/features/drawers/Referrals"
import Transactions from "@/components/features/drawers/Transactions"
import Topup from "@/components/features/drawers/Topup"
import { VisuallyHidden } from "@radix-ui/react-visually-hidden";
import { useQuery } from "@tanstack/react-query"
import { balanceService } from "@/services/balance.service"

export default function Work() {
    const { data: userBalance, isLoading: loadingUserBalance } = useQuery({
            queryKey: ['user balance'],
            queryFn: () => balanceService.getUserBalance()
    })

    const { data: investments, isLoading: loadingUserInvestments } = useQuery({
        queryKey: ['user investments'],
        queryFn: () => balanceService.investments()
    })

    const investmentsAmount = investments?.investments?.reduce((sum: number, investment: { amount: number }) => {
        return sum + investment.amount || 0;
    }, 0) || 0;

    return (
            <Card className='text-center p-2'>
                <CardContent className='flex items-center justify-around text-left'>
                    <div className='w-full font-bold text-xl'>
                        <Label>БАЛАНС</Label>
                        <p>
                            {loadingUserBalance ? 'Загрузка...' : userBalance?.balance.toFixed(3)} USDT
                        </p>
                    </div> 
                    <div className='w-full font-bold text-xl text-right'>
                        <Label>В РАБОТЕ</Label>
                        <p>
                            {loadingUserInvestments ? 'Загрузка...' : investmentsAmount?.toFixed(3)} USDT
                        </p>
                    </div>
                </CardContent>
                <CardFooter className='flex items-center justify-center pb-0'>
                    <Drawer>
                        <DrawerTrigger asChild>
                            <Button variant='ghost' className='h-full flex flex-col rounded-xl items-center text-xs p-2 [&_svg]:size-10'>
                                <MoveDown className="bg-background text-primary-foreground rounded-full p-2"/>
                                <p>ОТПРАВИТЬ</p>
                            </Button>
                        </DrawerTrigger>
                        <DrawerContent aria-describedby={undefined} className='flex items-center'>
                            <DrawerTitle>
                                <VisuallyHidden>Отправить</VisuallyHidden>
                            </DrawerTitle>
                            <Send />
                        </DrawerContent>
                    </Drawer>    
                    <Drawer>
                        <DrawerTrigger asChild>
                            <Button variant='ghost' className='h-full flex flex-col rounded-xl items-center text-xs p-2 [&_svg]:size-10'>
                                <Plus className="bg-background text-primary-foreground rounded-full p-2"/>
                                <p>ПОПОЛНИТЬ</p>
                            </Button>
                        </DrawerTrigger>
                        <DrawerContent aria-describedby={undefined} className='flex items-center'>
                            <DrawerTitle>
                                <VisuallyHidden>Пополнение</VisuallyHidden>
                            </DrawerTitle>
                            <Topup />
                        </DrawerContent>
                    </Drawer>   
                    <Drawer>
                        <DrawerTrigger asChild>
                            <Button variant='ghost' className='h-full flex flex-col rounded-xl items-center text-xs p-2 [&_svg]:size-10'>
                                <Users className="bg-background text-primary-foreground rounded-full p-2"/>
                                <p>РЕФЕРАЛЫ</p>
                            </Button>
                        </DrawerTrigger>
                        <DrawerContent aria-describedby={undefined} className='flex items-center'>
                            <DrawerTitle>
                                <VisuallyHidden>Рефераллы</VisuallyHidden>
                            </DrawerTitle>
                            <Referrals />
                        </DrawerContent>
                    </Drawer>
                    <Drawer>
                        <DrawerTrigger asChild>
                            <Button variant='ghost' className='h-full flex flex-col rounded-xl items-center text-xs p-2 [&_svg]:size-10'>
                                <Text className="bg-background text-primary-foreground rounded-full p-2"/>
                                <p>ТРАНЗАКЦИИ</p>
                            </Button>
                        </DrawerTrigger>
                        <DrawerContent aria-describedby={undefined} className='flex items-center'>
                            <DrawerTitle>
                                Транзакции
                            </DrawerTitle>
                            <Transactions />
                        </DrawerContent>
                    </Drawer>
                </CardFooter>
            </Card>
    )
}
