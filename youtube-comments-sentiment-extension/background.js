import {analyzeComments} from "./analyze.js";

chrome.runtime.onInstalled.addListener(() => {
  console.log('YouTube Comments Sentiment Analyzer Installed');
});

// chrome.webRequest.onCompleted.addListener(
//   callback: analyzeCurrentVideo,
// )

// async function analyzeCurrentVideo() {
//   console.log('URL changed, trying to analyze comments...');
//   analyzeComments();
// }

