'use client'

import BackButton from "@/components/features/telegram/BackButton";
import { Button } from "@/components/ui/common/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/common/card";
import { Label } from "@/components/ui/common/label";
import { Switch } from "@/components/ui/common/switch";
import { useProfile } from "@/hooks/useProfile";

export default function Settings() {
    const { user, isLoadingProfile } = useProfile();

    return (
        <>
            <BackButton />
            <Card className='text-center m-2'>
                <CardHeader>
                    <CardTitle>
                    Настройки
                    </CardTitle>
                </CardHeader>
                <CardContent className='space-y-4'>
                    <div className='flex items-center space-x-2'>
                        <Label htmlFor='airplane-mode'>Настройка</Label>
                        <Switch id='airplane-mode'/>
                    </div>
                    <div className='flex items-center space-x-2'>
                        <Label htmlFor='airplane-mode'>Настройка</Label>
                        <Switch id='airplane-mode'/>
                    </div>
                    <div className='flex items-center space-x-2'>
                        <Label htmlFor='airplane-mode'>Настройка</Label>
                        <Switch id='airplane-mode'/>
                    </div>
                    <div className='flex items-center space-x-2'>
                        <Label htmlFor='airplane-mode'>Настройка</Label>
                        <Switch id='airplane-mode'/>
                    </div>
                    <div className='grid grid-cols-2 gap-4'>
                        <Button className='rounded-xl shadow-none text-center'>
                            Кнопка
                        </Button>
                        <Button className='rounded-xl shadow-none text-center'>
                            Кнопка
                        </Button>
                        <Button className='rounded-xl shadow-none text-center'>
                            Кнопка
                        </Button>
                        <Button className='rounded-xl shadow-none text-center'>
                            Кнопка
                        </Button>
                    </div>
                    <div>
                        Русский
                    </div>
                    <div>
                        id: {isLoadingProfile ? 'Loading' : user?.telegram_id}
                    </div>
                </CardContent>
            </Card>
        </>
    );
    }