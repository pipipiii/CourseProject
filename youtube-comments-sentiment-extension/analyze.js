export async function getCurrentVideoId() {
  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  let re = /www\.youtube\.com\/watch\?v\=([^#&?]{11})/;
  let match = re.exec(tab.url);
  if (!match) {
    console.log("Not on a YouTube watch page: ", tab.url);
    return undefined;
  }
  let videoId = match[1];
  return videoId;
}

const SENTIMENT_API_KEY = 'API_KEY';  // Obfuscated
const SENTIMENT_FETCH_URL = 'https://youtube-comments-sentiment-gateway-8cfuu7oc.uc.gateway.dev/sentiment?key=' + SENTIMENT_API_KEY + "&videoId=";
export function analyzeComments(videoId, success_callback, failure_callback) {
  console.log("analyzing comments for video ", videoId, "...");
  fetch(SENTIMENT_FETCH_URL + videoId)
  .then(
    function(response) {
      if (response.status !== 200) {
        console.log('Error fetching comment sentiment: ', JSON.stringify(response));
        failure_callback();
        return;
      }

      // Examine the text in the response
      response.json().then(function(data) {
        success_callback(data);
        console.log("Done.");
        return;
      });
    }
  )
  .catch(function(err) {
    console.log('Fetch Error :-S', err);
    failure_callback();
    return;
  });
}
