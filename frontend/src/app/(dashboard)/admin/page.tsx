'use client'

import { Card, CardContent, CardHeader } from "@/components/ui/common/card";
import { userService } from "@/services/user.service";
import { useQuery } from "@tanstack/react-query";
import { Input } from "@/components/ui/common/input";
import { useState } from "react";


export default function Admin() {
    const [inputValue, setInputValue] = useState<string>("");

    const { data } = useQuery({
        queryKey: ['user info', inputValue],
        queryFn: () => {
            const id = parseFloat(inputValue);
            if (!isNaN(id)) {
                return userService.findUserById(id)
            }
            return Promise.resolve(null)
        },
        enabled: inputValue !== ""
    })

    return (
        <Card className='m-4'>
            <CardHeader>
                <Input placeholder="Введите id пользователя" value={inputValue} onChange={(e) => setInputValue(e.target.value)}/>
            </CardHeader>
            <CardContent className='flex flex-col space-y-1'>
                {data ? <div>
                            <p>{data?.id}</p>
                            <p>{data?.telegram_id}</p>
                            <p>{data?.username}</p>
                            <p>{data?.first_name}</p>
                            <p>{data?.last_name}</p>
                            <p>{data?.language_code}</p>
                            <p>{data?.photo_url}</p>
                            <p>{data?.created_at.toLocaleString()}</p>
                            <p>{data?.is_bot}</p>
                        </div> : 'Пользователь не найден'}
            </CardContent>
        </Card>
    );
}