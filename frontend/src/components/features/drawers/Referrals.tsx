'use client'

import * as React from "react"
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/common/card"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/common/tabs"
import { Button } from "@/components/ui/common/button"
import { ClipboardIcon } from "lucide-react"
import { useQuery } from "@tanstack/react-query"
import { referralService } from "@/services/referral.service"

export default function Referrals() {
  const { data, isLoading } = useQuery({
    queryKey: ['referral'],
    queryFn: () => referralService.getUserReferrals()
  })

  if (isLoading) return <div>Загрузка...</div>

  if (!data) return <div>Нет рефераллов</div>

  return (
      <div className='space-y-4 m-4'>
        <Card className='text-center'>
            <CardHeader>
                <CardTitle>
                    Доход по Реферальной системе
                </CardTitle>
            </CardHeader>
            <CardContent>
                0.00 USDT
            </CardContent>
        </Card>
        <Tabs defaultValue="system" className="w-[400px]">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="system">Система</TabsTrigger>
            <TabsTrigger value="referrals">Ваши рефералы</TabsTrigger>
          </TabsList>
          <TabsContent value="system">
            <Card className='text-center'>
              <CardHeader>
                <CardTitle>Поделитесь возможностью и увеличьте свои доходы с нашей реферальной программой!</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                  <Button className='w-full rounded-xl text-center m-2'>
                    {data.referral_link} <ClipboardIcon />
                  </Button>
                  <Button className='w-full rounded-xl text-center m-2'>
                    Пригласить
                  </Button>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="referrals">
            <Card className='text-center'>
              <CardHeader>
                <CardTitle>Ваши рефералы</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {data.invited_users.length > 0 ? (
                      data.invited_users.map((referral) => (
                          <Card key={referral.id} className="border-2 border-foreground">
                              <CardHeader>{referral.telegram_id}</CardHeader>
                              <CardContent>
                                  {referral.referral_link}
                              </CardContent>
                              <CardFooter>
                                  {referral.invited_users.map((user) => (
                                    <p key={user.user_id} className="m-2">{user.telegram_id}</p>
                                  ))}
                              </CardFooter>
                          </Card>
                      ))
                  ) : (
                      <p>Нет рефералов</p>
                  )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
  )
}