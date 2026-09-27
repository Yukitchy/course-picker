# course-picker — コースを選ばせるページの箱

ゲストに「A/B/Cから選んでね」と出すコース選択ページを、過去の実績から使い回すための道具。

- `engine/extract.py [pack]` 各ページの build.py からコースを吸い上げて `packs/<pack>/courses.json` を作る（ページには書き込まない）
- `engine/catalog.py [pack]` 台帳から一覧ページ `index.html` を作る
- `engine/find.py 語...` 台帳を検索（AND・部分一致・ジャンル名も可）
- ジャンルは `packs/<pack>/genres.json` のキーワードで自動で付く（経由地のホテル名は判定しない・店名は食べ歩きだけに使う）
- `engine/new.py <出力先> <key>...` 選んだコースで新しい選択ページのたたき台を作る（`page.json` の TODO を埋めて `python3 build.py`）

新しいページを出したら `packs/<pack>/sources.json` に1行足して extract → catalog。
他人が使う時は `packs/<自分>/sources.json` を作るだけ。
