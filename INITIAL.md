# AI討論プラットフォーム開発計画書

以下では、Firebase＋OpenAI APIなどを用いた「AI同士がある主題について討論するWebプラットフォーム」開発の全体計画をまとめます。  
実装支援ツールとして Google の自律型コーディングエージェント “Jules” を活用する前提で、Jules に通じるようタスク分割やリポジトリ構成、プロンプト例などを明示します。

---

## 1. プロジェクト概要・目的

- **概要**:  
  - 指定した「主題 (Topic)」について、複数のAI人格 (例：AI-A, AI-B, AI-C など) が順次または交互に投稿・返信し、あたかも討論が行われているかのようにログを生成・公開するWebプラットフォームを構築する。  
  - 人間はトピック設定および閲覧のみ行い、投稿そのものはすべてAI (OpenAI GPT 系モデルなど) のAPI呼び出しで自動生成する。

- **目的**:  
  - AI同士による議論を可視化し、多角的視点・反証を自動生成させて研究や教育、エンタメ用途に供する。  
  - プラットフォーム構築を通じて、Jules による自動コーディング支援の効果検証・開発効率向上の実践例を示す。

- **想定成果物**:  
  - Firebase Hosting 上に公開されるシンプルなWebアプリ  
  - Firestore でトピック＆メッセージ履歴データを管理  
  - Cloud Functions が Firestore イベントをトリガーに OpenAI API を呼び出し、AI人格の投稿を自動生成  
  - フロントエンドは HTML/JS (または React など) でリアルタイムに討論ログを表示  
  - GitHubリポジトリにソース一式をホスティングし、Jules でタスク管理・PR作成・テスト自動化を行う

---

## 2. 技術スタック

- **インフラ / クラウド**  
  - Firebase Hosting  
  - Firebase Firestore  
  - Firebase Cloud Functions (Node.js/TypeScript)  
- **AI API**  
  - OpenAI GPT-4 系 (もしくは用途に応じた他モデル)  
- **フロントエンド**  
  - シンプルHTML + JavaScript (Firebase Web SDK)  
    - もしくは React + Firebase SDK  
- **開発支援 / CI/CD**  
  - GitHub リポジトリ  
  - Jules: 自律型コーディングエージェント  
  - GitHub Actions (テスト自動実行・デプロイトリガー)  
- **ローカル開発環境**  
  - Node.js, npm/yarn  
  - Firebase CLI  
- **テスト**  
  - Cloud Functions のユニットテスト (例：Mocha + Chai)  
  - フロントエンドの軽量テスト（Jest や Puppeteer など、必要に応じて）

---

## 3. 開発ワークフローとJules活用方法

1. **リポジトリ初期化**  
   - GitHub リポジトリを作成  
   - `README.md`, `.gitignore`, Firebase 初期設定ファイルを用意  
   - Jules に対して:
     - Issue: “プロジェクト初期セットアップ: Firebase CLI 初期化、フォルダ構成作成”  
     - Jules が PR を作成 → 確認・マージ

2. **ディレクトリ構成策定**  
   - 例:
     ```
     /functions/        # Cloud Functions コード (TypeScript)
     /public/           # フロント静的ファイル (HTML, CSS, JS, Reactビルド成果物等)
     /scripts/          # 補助スクリプト
     README.md
     firebase.json
     package.json
     ```
   - Jules にタスク指示:
     - “ディレクトリ構成を上記のように作成し、package.json に必要な依存（firebase-functions, firebase-admin, openai など）を追加するPRを作ってください。”

3. **Firestore スキーマ設計**  
   - コレクション例:
     - `topics` コレクション:
       - ドキュメント ID: 自動生成 or スラッグ  
       - フィールド: `title` (string), `description` (string), `createdAt`, `config` (例: AI人格リスト, 最大ラウンド数, 討論ルール等)  
       - サブコレクション: `messages`
         - ドキュメント ID: 自動生成  
         - フィールド: `content` (string), `author` (string: AI人格名), `timestamp`, `parentMessageId` (省略可・スレッド化用)  
   - Jules タスク:
     - “Firestore コレクション/ドキュメントスキーマをドキュメントにまとめ、TypeScriptコード上で型定義（interface）を作成するPRを作ってください。”

4. **Cloud Functions: AI呼び出しロジック**  
   - トリガー: `topics/{topicId}/messages/{messageId}` 作成時  
   - 処理:
     1. 新規メッセージが来たら、次に応答すべきAI人格を決定 (交互 or ランダム or 事前設定)  
     2. Prompt を組み立て:
        - これまでのメッセージ履歴 or 最新メッセージのみ  
        - 「以下は“主題: {title}”についての討論です。これまでの発言: ... 次に {次のAI人格} として反論・補強を述べてください。」など  
     3. OpenAI API 呼び出し (非同期エラー処理・レート制御に注意)  
     4. 生成結果を Firestore `topics/{topicId}/messages` に追加  
   - Jules タスク:
     - “Cloud Functions の雛形を作成し、Firestore トリガーから OpenAI API を呼び出す TypeScriptコードを書いてください。エラー時の再試行ロジックやログ出力も含めてください。”

5. **フロントエンド: 討論ログ表示**  
   - Firebase Web SDK (firestore) でリアルタイムリスナー登録  
   - UI:
     - トピック一覧ページ: 各トピックのタイトル・簡易説明を列挙  
     - トピック詳細ページ: タイトルと説明を表示し、`messages` をタイムスタンプ順にリスト表示  
       - 各メッセージに: AI人格名、コンテンツ、投稿時間  
       - 必要に応じて: メッセージに対する返信フローを視覚化 (簡易スレッド表示)  
   - Jules タスク:
     - “フロントエンドの HTML/JS (あるいは React サンプル) を作成し、Firestore からリアルタイムにメッセージを購読してレンダリングするコードを追加するPRを作ってください。”

6. **トピック作成機能**  
   - 管理者または人間ユーザが新規トピックを作成する画面／手順  
   - Firestore に `topics/{newTopicId}` ドキュメントを追加し、初回メッセージを自動生成トリガーする仕組み  
   - Jules タスク:
     - “トピック作成フォーム（フロント側）と、それを Firestore に保存するロジックを実装するPRを作成してください。作成時に Cloud Function でAI初回投稿を起動する仕組みも含めて。”

7. **AI人格管理・設定**  
   - `config` フィールド内に AI人格リストを配列で定義 (例: `["AI-A: 保守的視点", "AI-B: 革新的視点", "AI-C: 中立分析者"]`)  
   - Cloud Functions で次の投稿者を決定するロジック: 設定順に交互、またはスコアリングに応じて  
   - Jules タスク:
     - “AI人格設定を Firestore ドキュメントから読み込み、投稿順決定ロジックを実装するコードを追加してください。”

8. **制御機構・ルール**  
   - 最大投稿数（ラウンド数）制限: 無限ループ防止  
   - 一定時間待機後に次投稿: リアルタイム即応 or 遅延スケジュール  
   - エラーハンドリング: API失敗時のリトライ or 通知  
   - Jules タスク:
     - “投稿ラウンド上限やタイムアウト処理、再試行ポリシーを含む設計をドキュメント化し、コードに反映するPRを作成してください。”

9. **テスト・CI**  
   - Cloud Functions のユニットテスト: Firestore トリガーイベントをモックし、OpenAI呼び出し部分はモック化して正常/異常ケースを検証  
   - フロントテスト: UI の描画・Firestore購読のモックテスト  
   - GitHub Actions:
     - プッシュ・PR時にテスト自動実行  
     - main ブランチマージ時に Firebase デプロイ（またはステージング環境へのデプロイ）  
   - Jules タスク:
     - “CI設定 (GitHub Actions) を追加し、Cloud Functions とフロントのテストスクリプトを実行するワークフローを作成するPRを作ってください。”

10. **デプロイ・運用**  
    - Firebase Hosting へのデプロイ: `firebase deploy --only hosting,functions`  
    - 環境変数管理: OpenAI APIキー等を Firebase Functions の環境設定に登録 (`firebase functions:config:set openai.key="..."`)  
    - モニタリング: Firebase コンソールで Function エラーや実行時間を監視  
    - エラー通知: Slack/Webhook 連携で失敗時にアラート  
    - Jules タスク:
      - “デプロイ手順ドキュメント (README) を整備し、GitHub Actions で自動デプロイフローを追加するPRを作成してください。”  

11. **ドキュメント整備**  
    - README.md: セットアップ手順、環境変数設定、ローカル開発手順、デプロイ手順、アーキテクチャ図  
    - Developer Guide: コード構造説明、Jules へのタスク出し方法例、テストガイド  
    - User Guide: プラットフォーム利用方法 (閲覧・トピック申請フローなど)  
    - Jules タスク:
      - “README.md と Developer Guide のドラフトを作成するPRを出してください。”

12. **拡張機能・将来要件**  
    - 人間ユーザが質問や途中参戦できる機能  
    - 投票・評価機能: 有益なAI発言に“いいね”やスコアをつける  
    - 討論の可視化: 発言間の関係をグラフ表示  
    - 複数モデル連携: GPT-4 vs 他モデルで討論  
    - Jules タスク:
      - “評価機能の設計文書を作成し、フロント／バックエンドの雛形コードPRを作成してください。”

---

## 4. Jules への具体的タスク例・プロンプト例

以下は GitHub Issues (またはプロジェクトボード) に書くタスク例と、Jules に与えるプロンプト例です。

1. **プロジェクト初期セットアップ**  
   - **Issue タイトル**: “Firebaseプロジェクト初期化とディレクトリ構成”  
   - **Issue 内容 (Jules向け)**:
     ```
     - Firebase CLI でプロジェクト初期化 (functions, hosting を有効化)
     - ディレクトリ構成:
       /functions
       /public
       README.md（概要、セットアップ手順）
       package.json (共通依存)
     - package.json に: firebase-admin, firebase-functions, openai, cors などを追加
     - GitHub Actions 用のワークフローファイル雛形を追加 (.github/workflows/ci.yml)
     - PRを作成し、変更点の説明を記載
     ```
   - **期待結果**: PR が作られ、手動確認後マージ

2. **Firestore スキーマ定義**  
   - **Issue タイトル**: “Firestore スキーマ設計と型定義”  
   - **Issue 内容**:
     ```
     - topics コレクションのスキーマをドキュメント化 (title, description, config, createdAt)
     - messages サブコレクションのスキーマ定義 (content, author, timestamp, parentMessageId)
     - TypeScript interface を functions/src/types.ts に追加
     - スキーマ変更時のマイグレーション手順メモを README に追記
     ```
   - **期待結果**: 型定義ファイル + ドキュメントが追加される

3. **Cloud Functions: AI呼び出しロジック作成**  
   - **Issue タイトル**: “新規メッセージ投稿時にOpenAI呼び出しを行うCloud Function作成”  
   - **Issue 内容**:
     ```
     - Firestore onCreate トリガー: topics/{topicId}/messages/{messageId}
     - トピック情報 (title, config) と過去メッセージを取得
     - 次のAI人格を決定するロジック (例: config.aiOrder に従って交互)
     - Prompt を組み立て：
       「主題: ${title}。これまでの発言: ${history}。あなたは${nextAuthor}として反論・補強を述べてください。」
     - OpenAI API 呼び出し (ChatCompletion) 部分を実装
     - 生成結果を messages サブコレクションに追加 (author: nextAuthor, timestamp: admin.firestore.FieldValue.serverTimestamp())
     - エラー処理: API失敗時ログ出力＋再試行 or エラーメッセージ投稿
     - functions/src/index.ts に実装し、デプロイ可能状態に
     ```
   - **期待結果**: テスト可能なFunctionコード + ユニットテスト

4. **フロント: 討論ログ一覧表示**  
   - **Issue タイトル**: “フロントエンド: Topic詳細ページ実装”  
   - **Issue 内容**:
     ```
     - public/index.html (または React の画面) に Topic詳細ページテンプレート作成
     - Firebase SDK 初期化スクリプトを読み込み
     - Firestore の topics/{topicId}/messages をリアルタイム購読し、タイムスタンプ順にリスト表示
     - 各メッセージ: author, content, 時刻表示。スタイルはシンプルCSS or Tailwindなど。
     - 新規トピック作成ページへのリンク設置
     ```
   - **期待結果**: ローカルでも動作確認できるUI

5. **トピック作成フォーム実装**  
   - **Issue タイトル**: “フロント: トピック作成機能”  
   - **Issue 内容**:
     ```
     - public/new_topic.html (または Reactコンポーネント) でフォーム作成 (title, description, AI人格設定など)
     - 送信時に Firestore topics コレクションへ保存
     - 保存完了後、Cloud Function で初回AI投稿が行われることを想定
     - バリデーションやエラーハンドリング（必須入力チェックなど）
     ```
   - **期待結果**: トピック作成から初回AI投稿まで動作確認可能

6. **CI/CD セットアップ**  
   - **Issue タイトル**: “GitHub Actions: テスト＆デプロイワークフロー”  
   - **Issue 内容**:
     ```
     - push/PR 時に Cloud Functions のユニットテストを実行
     - フロントテスト (あれば) を実行
     - mainブランチへのマージ時に Firebase CLI で deploy 実行
     - シークレット管理: OpenAI APIキーや Firebase サービスアカウントは GitHub Secrets に登録
     - デプロイステータス通知 (Slack/メール) 連携設定（任意）
     ```
   - **期待結果**: プロジェクトが main マージで自動デプロイされる

7. **テスト実装**  
   - **Issue タイトル**: “Cloud Functions ユニットテスト実装”  
   - **Issue 内容**:
     ```
     - Firestore トリガー関数をモック Firestore イベントで呼び出し、OpenAI呼び出し部分は jest.mock や sinon でスタブ化
     - 正常ケース: 期待したメッセージが追加されることを検証
     - 異常ケース: APIエラー時の再試行ロジックやログ出力を検証
     - Frontend: Firestore購読部分をモックして表示ロジックをテスト（可能な範囲で）
     ```
   - **期待結果**: テストが自動実行され、品質担保

---

## 5. 具体的な成果イメージ

- **サイトURL例**: `https://your-project.web.app/`
- **トップページ**:  
  - 「AI討論プラットフォームへようこそ」  
  - 既存トピック一覧 (カード表示: タイトル・説明・最新投稿時刻)  
  - 「新規トピック作成」ボタン

- **トピック詳細ページ**:  
  - 上部に主題タイトルと説明  
  - AI人格ごとのアイコンや色分け (任意)  
  - 投稿ログ: タイムスタンプ順に吹き出し或いはカードで表示  
    - 吹き出しに「AI-A (保守的視点) 10:01:23」: 内容本文  
    - 次に「AI-B (革新的視点) 10:02:10」: 反論内容  
    - …と続く討論形式  
  - 「次のAI投稿を手動トリガー」ボタン（自動投稿が一定間隔で行われる設定も可）  
  - 投稿数が上限に達すると「討論終了」表示

- **管理画面（任意）**:  
  - トピック一覧の管理機能 (不要なら省略)  
  - 投稿上限やAI人格一覧の設定変更

- **ログ・監視画面**:  
  - Cloud Functions のエラー履歴確認  
  - Firestore データ状況 (参加AI人数、投稿数など統計ダッシュボード)

---

## 6. セキュリティ・運用面留意点

- **APIキー管理**:  
  - OpenAI APIキーは Firebase Functions 環境変数に保管  
  - GitHub等にハードコーディングしない  
- **Firestore ルール**:  
  - 公開トピックは誰でも読み取り可  
  - トピック作成／設定変更は管理者のみとするなら認証＋ルールを設定  
  - AIの書き込みは Cloud Functions 経由なので、クライアントから直接メッセージ書き込み禁止ルールを設ける
- **レート制御**:  
  - OpenAI API の呼び出し回数制御 (討論ラウンド設定で上限を明確化)  
- **コスト管理**:  
  - Cloud Functions 実行時間とAPIコール数をモニタリングし、予算に収まるよう設定  
- **フェールセーフ**:  
  - API失敗時に人間が確認できるログ記録 or 管理者通知  
- **プライバシー**:  
  - 投稿内容は一般公開前提。特に人間データを含まない設計なので問題は少ないが、必要に応じて利用規約等で説明。

---

## 7. 開発スケジュール（例・マイルストーン）

1. **Week 1**  
   - リポジトリセットアップ & Julesタスクで初期構成完了  
   - Firestoreスキーマ確定 & 型定義  
   - Cloud Functions雛形作成  
   - フロントの骨組み作成

2. **Week 2**  
   - AI呼び出しロジック詳細実装 & テスト  
   - トピック作成機能実装  
   - フロントでリアルタイム表示動作確認  
   - CI/CDパイプライン整備

3. **Week 3**  
   - UI改善 (デザイン調整、AI人格表示など)  
   - エラーハンドリング強化・ログ通知設定  
   - セキュリティルール調整  
   - パフォーマンス確認 (大量投稿シミュレーション等)

4. **Week 4**  
   - ベータ公開 & 社内/知人へのフィードバック募集  
   - バグ修正・改善  
   - ドキュメント整備 (User Guide, Developer Guide)  
   - 正式運用開始

5. **以降**  
   - 機能追加 (評価機能、可視化など)  
   - 複数モデル・多言語対応  
   - スポンサーシップや商用展開検討

---

## 8. Jules活用ポイントまとめ

- **Issueごとにタスクを細かく分割**し、JulesにPR作成を依頼。レビュー・マージして品質担保。  
- **コード理解を助ける型定義やコメント**をJulesに書かせる。  
- **テストコードの自動生成**をJulesに頼み、CIで自動実行。  
- **ドキュメント (README, 設計書) のドラフト作成**をJulesに任せ、レビューして完成度を高める。  
- **デプロイ設定やGitHub Actions設定**もJulesにPR作成させることで開発効率向上。

**注意**: 最終的な品質チェック・セキュリティレビュー・APIキー管理設定などは必ず人の目で確認する。

---

## 9. 開発準備：Jules利用手順例

1. **GitHub リポジトリ作成**  
   - “Create repository” で新規リポジトリを用意  
   - 初期 README だけ置く

2. **Julesセットアップ**  
   - GitHub 連携設定完了  
   - Jules パネルでリポジトリをインポート  
   - “初期タスク: Firebase初期化＆ディレクトリ構成作成” をIssueで作成し、JulesにPRを実行させる

3. **Firebase プロジェクトと連携**  
   - Firebase CLI でローカルに設定ファイルを取得  
   - Jules タスクで Firestore ルールファイル / 初期 Cloud Functions フォルダ作成を依頼

4. **継続的タスク依頼**  
   - 各機能ごとに Issue を作成 → Jules がPR → レビュー → マージ  
   - テスト失敗や修正要望があれば Issue コメントで指示し、Julesに再修正PRを出させる

---

## 10. リスク・留意点

- **AIコスト増大**: 討論が長くなるとOpenAI APIコールが増え、コスト上昇。ラウンド数制限や要約メカニズムを検討する。  
- **無限ループ防止**: Cloud Functions トリガーでAIが再度トリガーを呼ぶループに注意。Firestoreにフラグを設けたり、投稿種別で初回/応答を制御する。  
- **レスポンス品質管理**: AIの生成内容をそのまま公開すると、不適切発言の可能性がある。フィルタリング機構やモニタリングを検討。  
- **Jules依存の注意**: 自動生成されたコードの品質チェックは必須。セキュリティ脆弱性や設計ミスがないかレビューを欠かさない。  
- **APIキー漏洩防止**: 環境変数やシークレット管理は厳密に。JulesやCIにも漏洩しないよう設定。

---

## 11. まとめ

- 本計画書では、Firebase + OpenAI API を用いた「AI討論プラットフォーム」の開発計画を記載。  
- Jules を自律型コーディングエージェントとして活用し、Issue → PR の流れで効率的にコード実装、テスト、ドキュメント整備を進める。  
- 最終的に、公開可能なWebアプリが出来上がり、指定トピックに対してAI同士が自動で討論を行い、そのログを閲覧可能とする。  
- セキュリティ・コスト管理・ループ防止・品質チェックなど運用面の注意事項も併せて検討。  
- 開発開始前にリポジトリとFirebaseプロジェクトを用意し、早めにJulesに基本構成作成を依頼することでスムーズなスタートを図る。

---

以上が計画書のMD形式全文です。Julesにタスクを投げる際のIssueテンプレートやプロンプト例も含めています。  
これをもとにリポジトリ初期化し、Julesを活用してコーディングを進めてみてください。  
出来上がるものは、Firebase上で稼働するAI討論プラットフォームのソース一式と、Julesによる自動PRワークフローの実績です。  

