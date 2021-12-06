import {analyzeComments, getCurrentVideoId} from "./analyze.js";

// Button to analyze the current page
let analyzeButton = document.getElementById("analyze");
let videoIdElement = document.getElementById("video-id");
let analyzingElement = document.getElementById("analyzing");
let sentimentElement = document.getElementById("sentiment");

window.onload = async function() {
  let videoId = await getCurrentVideoId();
  videoIdElement.innerHTML = videoId;
}

analyzeButton.addEventListener("click", async () => {
  // let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  // console.log(tab.url);
  // chrome.scripting.executeScript({
  //   target: { tabId: tab.id },
  //   function: analyzeComments,
  //   args: [tab.url],
  // });

  let videoId = await getCurrentVideoId();
  toggleDisplay(true);
  videoIdElement.innerHTML = videoId;
  analyzeComments(videoId, (data) => {
    toggleDisplay(false);
    // sentimentElement.innerHTML = JSON.stringify(data);
    console.log(JSON.stringify(data));
    displaySentiment(data);
  },
  () => {
    analyzeButton.style.display = "block";
    sentimentElement.innerHTML = "Oops, something went wrong...try again?";
  });
});

function toggleDisplay(analyzing) {
  if (analyzing) {
    analyzeButton.style.display = "none";
    sentimentElement.style.display = "none";
    analyzingElement.style.display = "block";
  } else {
    analyzeButton.style.display = "block";
    sentimentElement.style.display = "block";
    analyzingElement.style.display = "none";
  }
}

function displaySentiment(data) {
    // Overall sentiment
    setSentimentScore(data["overallSentiment"], "overall-scale-marker", "overall-sentiment-score");

    // Comments favorings
    setSentimentScore(data["topicSentiments"]["0"]["sentiment"], "topic0-scale-marker", "topic0-sentiment-score");
    setSentimentScore(data["topicSentiments"]["1"]["sentiment"], "topic1-scale-marker", "topic1-sentiment-score");
    setTopicKeywords(data["topicSentiments"]["0"]["topic"], "topic0-keywords");
    setTopicKeywords(data["topicSentiments"]["1"]["topic"], "topic1-keywords");

}

function setSentimentScore(scoreData, markerElementId, scoreElementId) {
    let sentimentScore = Math.round(Number(scoreData) * 100);
    let markerElement = document.getElementById(markerElementId);
    markerElement.style.left = (sentimentScore + 100) / 2 + "%";

    let sentimentScoreDisplay = sentimentScore.toString() + "%";
    let scoreElement = document.getElementById(scoreElementId);
    scoreElement.innerHTML = sentimentScoreDisplay;
}

function setTopicKeywords(topicData, keywordsElementId) {
    let keywordsElement = document.getElementById(keywordsElementId);
    let keywords = [];
    for (let topic of topicData) {
        keywords.push('<span class="keyword" style="opacity:' + Math.max(Math.min(Number(topic[1]) * 5 + 0.7, 1), 0) + '">' + topic[0] + '</span>');
    }
    keywordsElement.innerHTML = keywords.join("");
}

// // The body of this function will be execuetd as a content script inside the
// // current page
// function analyzeComments(url) {
//   let re = /www\.youtube\.com\/watch\?v\=([^#&?]{11})/;
//   let match = re.exec(url);
//   if (!match) {
//     console.log("Not on a YouTube watch page.");
//     return;
//   }
//   let videoId = match[1];
//   console.log(videoId);
//   videoIdElement.value = videoId;
// }
