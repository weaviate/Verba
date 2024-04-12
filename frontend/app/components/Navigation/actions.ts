'use server'

export async function getGitHubStars(): Promise<any> {
    try {
        const response = await fetch('https://api.github.com/repos/weaviate/verba', {
            method: 'GET',
        });

        if (response) {
            console.log(response)
        }
        return response;
    } catch (error) {
        console.error("Failed to perform search:", error);
        return null
    }
}