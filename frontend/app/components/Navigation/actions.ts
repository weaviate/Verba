export async function getGitHubStars(): Promise<any> {
    try {
        const response: any = await fetch('https://api.github.com/repos/weaviate/verba', {
            method: 'GET',
        });

        const data: any = await response.json()

        if (data) {
            console.log("Stars " + data.stargazers_count)
            return data.stargazers_count
        } else {
            return 0
        }
    } catch (error) {
        console.error("Failed to perform search:", error);
        return 0
    }
}