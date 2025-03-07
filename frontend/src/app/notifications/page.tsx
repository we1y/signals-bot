'use client'

import BackButton from "@/components/features/telegram/BackButton";
import { Card, CardContent, CardHeader } from "@/components/ui/common/card";
import { Label } from "@radix-ui/react-label";
import { ArrowLeft } from "lucide-react";


export default function Notifications() {
    const notifications = [
        {
            id: 1,
            name: 'Уведомление 1'
        },
        {
            id: 2,
            name: 'Уведомление 2'
        },
        {
            id: 3,
            name: 'Уведомление 3'
        },
        {
            id: 4,
            name: 'Уведомление 4'
        },
        {
            id: 5,
            name: 'Уведомление 5'
        },
        {
            id: 6,
            name: 'Уведомление 6'
        }
    ]

    return (
        <>
            <BackButton />
            <Card className='shadow-none text-center m-2 p-4'>
                <CardHeader className="space-y-8">
                    {notifications.map(notification => 
                        <Label key={notification.id}>
                            {notification.name}
                        </Label>
                        )
                    }
                </CardHeader>
            </Card>
        </>
    );
}