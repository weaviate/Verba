export const detectHost = async (): Promise<string> => {
  const checkUrl = async (url: string): Promise<boolean> => {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP status ${response.status}`);
      }
      return true;
    } catch (error) {
      console.error(`Failed to fetch from ${url}:`, error);
      return false;
    }
  };

  const localUrl = "http://localhost:8000/api/health";
  const rootUrl = "/api/health";

  const isLocalHealthy = await checkUrl(localUrl);
  if (isLocalHealthy) {
    return "http://localhost:8000";
  }

  const isRootHealthy = await checkUrl(rootUrl);
  if (isRootHealthy) {
    return "";
  }

  throw new Error("Both health checks failed, please check the Verba Server");
};
