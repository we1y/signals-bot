import { useQuery } from '@tanstack/react-query'

import { userService } from '@/services/user.service'

export function useProfile() {
	const { data: user, isLoading: isLoadingProfile } = useQuery({
		queryKey: ['profile'],
		queryFn: () => userService.getUser()
	})

	return { user, isLoadingProfile }
}