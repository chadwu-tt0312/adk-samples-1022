+ 請根據本專案，寫一份 markdown 格式的 "MLE-STAR-使用說明.md"
+ 如果有需要補充或討論確認的項目請提出討論再開始撰寫報告

1. 目標讀者-技術人員（負責部署與維護）
2. 安裝與部署
 	+ Kubernetes Helm
		+ 如果沒有現成的 Kubernetes Helm 部署檔案。參考 docker-compose 的設定，新建 Kubernetes Helm 的部署檔案。
		+ 如果沒有 docker-compose 檔案。請根據專案中使用的安裝與部署方式自行決定安裝與部署方式。
 	+ 儲存使用 nfs
		+ 使用 Kubernetes Helm 部署時才需要 nfs。
3. 內容範圍
 	+ 基本操作
 	+ 進階設定（LLM 整合）
 	+ 故障排除
4. 範例與截圖
	+ 如果無法產生圖片(或者專案中沒有範例圖片可以直接使用)，可以用文字描述來替代，但請註記以便後續添加圖片。
5. 環境變數設定
    + 詳細說明所有環境變數
6. adk_fix.py adk_runner.py run_task.py 等檔案是後來自行建立，用來測試用。專案分析時可以略過。
