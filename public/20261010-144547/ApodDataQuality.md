# ApodDataQuality

Version `20261010-144547`, built from https://apod.tw/ (articles 20190411 to 20251004).

## 1. Articles

- 1,511 daily articles in `sitemap.xml`
- 1,511 on the 7 pages of the `/daily/` listing
- 1,511 in their union, 1,511 fetched, 0 answering 404
- 1,511 with a 詞彙學習 table, 0 with no 詞彙學習 heading, 0 with the heading but no table
- 0 with a table of no rows

### Titles

Every article's title is read from its `[漢羅]`, `[POJ]`, `[KIP]` and `[English]` headings. Articles lacking one or more (an empty heading counts as lacking): 7.

| Article | Missing |
|---|---|
| [20210604](https://apod.tw/daily/20210604/) | EngBun |
| [20220211](https://apod.tw/daily/20220211/) | KipUnicode |
| [20220829](https://apod.tw/daily/20220829/) | KipUnicode |
| [20230331](https://apod.tw/daily/20230331/) | KipUnicode |
| [20240527](https://apod.tw/daily/20240527/) | HanLoTaibunPoj |
| [20240730](https://apod.tw/daily/20240730/) | PojUnicode |
| [20250729](https://apod.tw/daily/20250729/) | PojUnicode |

## 2. Tables

- 1,511 tables have the columns `漢羅`, `POJ`, `KIP`, `華語`, `English`
- 0 have other columns (cells are matched by header name; a header not in the list above is dropped)
- 0 rows have a different number of cells than their table has headers (kept: cells matched left to right)

## 3. Rows

13,587 rows in `ApodSului`, 4,943 distinct `PojUnicode`, 4,091 distinct `HanLoTaibunPoj`.

| Column | Rows filled |
|---|---|
| `PojUnicode` | 13,581 |
| `PojInput` | 13,581 |
| `KipUnicode` | 13,575 |
| `KipInput` | 13,575 |
| `HanLoTaibunPoj` | 13,587 |
| `HoaBun` | 13,582 |
| `EngBun` | 13,578 |
| `LaigoanMia` | 13,587 |
| `LaigoanBangchi` | 13,587 |

### Rows with an empty cell

29 rows.

| Article | Empty | HanLoTaibunPoj | PojUnicode | KipUnicode |
|---|---|---|---|---|
| [20210719](https://apod.tw/daily/20210719/) | EngBun | `半人馬座 Alpha 星` | `Poàn-jîn-má-chō` | `Puàn-jîn-má-tsō` |
| [20210807](https://apod.tw/daily/20210807/) | EngBun | `毅力號探測車` | `Gē-le̍k-hō thàm-chhek-chhia` | `Gē-li̍k-hō thàm-tshik-tshia` |
| [20211211](https://apod.tw/daily/20211211/) | EngBun | `BICEP 望遠鏡` | `BICEP bōng-oán-kiàⁿ` | `BICEP bōng-uán-kiànn` |
| [20211224](https://apod.tw/daily/20211224/) | EngBun | `電磁波頻譜` | `tiān-chû-pho pîn-phó͘` | `tiān-tsû-pho pîn-phóo` |
| [20220108](https://apod.tw/daily/20220108/) | EngBun | `北極星` | `Pak-ke̍k-chhiⁿ` | `Pak-ki̍k-tshinn` |
| [20220205](https://apod.tw/daily/20220205/) | EngBun | `哈伯太空望遠鏡` | `Ha-peh Thài-khong-bōng-oán-kiàⁿ` | `Ha-peh Thài-khong-bōng-uán-kiànn` |
| [20220331](https://apod.tw/daily/20220331/) | EngBun | `地面望遠鏡` | `tē-bīn-bōng-oán-kiàⁿ` | `tē-bīn-bōng-uán-kiànn` |
| [20220925](https://apod.tw/daily/20220925/) | KipUnicode | `M16` | `M cha̍p-la̍k` | `` |
| [20230402](https://apod.tw/daily/20230402/) | PojUnicode | `觀星者` | `` | `kuan-sing-tsiá` |
| [20230616](https://apod.tw/daily/20230616/) | PojUnicode, KipUnicode, HoaBun | `Baltic 海` | `` | `` |
| [20230909](https://apod.tw/daily/20230909/) | EngBun | `長蛇座 Sigma 流星雨` | `Tn̂g-Siâ-chō Sigma Liû-chheⁿ-hō͘` | `Tn̂g-Siâ-tsō Sigma Liû-tshenn-hōo` |
| [20231027](https://apod.tw/daily/20231027/) | PojUnicode | `Encke 彗星` | `` | `Encke Hui-tshenn` |
| [20231118](https://apod.tw/daily/20231118/) | KipUnicode | `獵戶座太空船` | `La̍h-hō͘-chō Thài-khong-chûn` | `` |
| [20240106](https://apod.tw/daily/20240106/) | KipUnicode | `彗星 67P` | `hūi-chheⁿ 67P` | `` |
| [20240111](https://apod.tw/daily/20240111/) | EngBun | `北極星` | `Pak-ke̍k-chhiⁿ` | `Pak-ki̍k-tshinn` |
| [20240118](https://apod.tw/daily/20240118/) | PojUnicode | `海拔` | `` | `hái-pua̍t` |
| [20240118](https://apod.tw/daily/20240118/) | HoaBun | `捲螺仔星系` | `kńg-lê-á seng-hē` | `kńg-lê-á sing-hē` |
| [20240202](https://apod.tw/daily/20240202/) | KipUnicode | `肚胿仔` | `tō͘-koai-á` | `` |
| [20240211](https://apod.tw/daily/20240211/) | HoaBun | `Atlantis 號太空梭` | `Atlantis hō thài-khong-so` | `Atlantis hō thài-khong-so` |
| [20240217](https://apod.tw/daily/20240217/) | PojUnicode | `頂層大氣` | `` | `tíng-tsàn tāi-khì` |
| [20240311](https://apod.tw/daily/20240311/) | KipUnicode | `藍色目屎` | `Nâ-sek Ba̍k-sái` | `` |
| [20240603](https://apod.tw/daily/20240603/) | KipUnicode | `NGC 2403` | `NGC jī-sù-khòng-sam` | `` |
| [20240709](https://apod.tw/daily/20240709/) | KipUnicode | `極地中氣層雲` | `Ke̍k-tē Tiong-khì-chân hûn` | `` |
| [20240718](https://apod.tw/daily/20240718/) | KipUnicode | `小人馬座恆星雲` | `Sió Jîn-má-chō Hêng-chhiⁿ-hûn` | `` |
| [20240912](https://apod.tw/daily/20240912/) | PojUnicode, KipUnicode | `獨立行星` | `` | `` |
| [20250818](https://apod.tw/daily/20250818/) | HoaBun | `塗粉帶` | `thô͘-hún-tòa` | `thôo-hún-tuà` |
| [20250823](https://apod.tw/daily/20250823/) | KipUnicode | `月圓` | `goe̍h-îⁿ` | `` |
| [20250823](https://apod.tw/daily/20250823/) | KipUnicode | `直徑` | `ti̍t-kèng` | `` |
| [20250911](https://apod.tw/daily/20250911/) | HoaBun | `月全食` | `goe̍h-choân-si̍t` | `gue̍h-tsuân-si̍t` |

### POJ cells with a piece that is not Pe̍h-ōe-jī

9 rows.

| Article | Cell | Pieces |
|---|---|---|
| [20210829](https://apod.tw/daily/20210829/) | `Siang Sió-kiânn-tshinn Tiông-sin-tīng-hiòng Tshik-giām` | `kiânn` |
| [20211214](https://apod.tw/daily/20211214/) | `HH lio̍k-lio̍k柱-lio̍k thian-thé` | `lio̍k柱` |
| [20221017](https://apod.tw/daily/20221017/) | `hok-siā-suànn` | `suànn` |
| [20230603](https://apod.tw/daily/20230603/) | `hū-phìnn` | `phìnn` |
| [20231110](https://apod.tw/daily/20231110/) | `Gio̍k-hu-tsō` | `tsō` |
| [20250721](https://apod.tw/daily/20250721/) | `Uí-peh Thài-khong Bōng-uán-kiànn` | `kiànn` |
| [20250721](https://apod.tw/daily/20250721/) | `hun-tsú hûn` | `tsú` |
| [20250922](https://apod.tw/daily/20250922/) | `pak-puànn-kiû` | `puànn` |
| [20250922](https://apod.tw/daily/20250922/) | `lâm-puànn-kiû` | `puànn` |

### KIP cells with a piece that is not KPL

74 rows.

| Article | Cell | Pieces |
|---|---|---|
| [20210117](https://apod.tw/daily/20210117/) | `tiān-chiunn phùn-lâu` | `chiunn` |
| [20210210](https://apod.tw/daily/20210210/) | `sī-bāng-mo̍͘h` | `mo̍͘h` |
| [20210211](https://apod.tw/daily/20210211/) | `Thian-gô-chō` | `chō` |
| [20210311](https://apod.tw/daily/20210311/) | `sing-tsè-thô͘-hún-lia̍p` | `thô͘` |
| [20210423](https://apod.tw/daily/20210423/) | `Kok-chè-thài-khong-chām` | `chè`, `chām` |
| [20210512](https://apod.tw/daily/20210512/) | `kiânn-tshinn-kan thô͘-hún-lia̍p` | `thô͘` |
| [20210524](https://apod.tw/daily/20210524/) | `iûnn-á kiânn-tshiⁿ` | `tshiⁿ` |
| [20210606](https://apod.tw/daily/20210606/) | `lji̍t-tsuân-si̍t` | `lji̍t` |
| [20210609](https://apod.tw/daily/20210609/) | `Tshiau-kip hue-hueh-gue̍he` | `gue̍he` |
| [20210718](https://apod.tw/daily/20210718/) | `tn̂g-tu-îⁿ sing-hē` | `îⁿ` |
| [20210721](https://apod.tw/daily/20210721/) | `sng-sò͘` | `sò͘` |
| [20211006](https://apod.tw/daily/20211006/) | `Chhiâ-ko-hîng sing-thuân` | `Chhiâ` |
| [20211006](https://apod.tw/daily/20211006/) | `Chhiâ-to-hîng sing-thuân` | `Chhiâ` |
| [20220602](https://apod.tw/daily/20220602/) | `thàu-chá-chhiⁿ` | `chá` |
| [20220610](https://apod.tw/daily/20220610/) | `Sik-lú-chō` | `chō` |
| [20220614](https://apod.tw/daily/20220614/) | `kē kuí-tō se̍h-tē-uī-chhiⁿâ` | `chhiⁿâ` |
| [20220708](https://apod.tw/daily/20220708/) | `hî-gán-kiàⁿ-thâu` | `kiàⁿ` |
| [20220723](https://apod.tw/daily/20220723/) | `Lêng-chēng-hái` | `chēng` |
| [20220814](https://apod.tw/daily/20220814/) | `bî-tiōng-le̍k thàu-kiàⁿ-hāu-èng` | `kiàⁿ` |
| [20220816](https://apod.tw/daily/20220816/) | `Ing-sian-tsō liû-tshinn-hō͘lta Lâm Liû-tshinn-hōo` | `hō͘lta` |
| [20220827](https://apod.tw/daily/20220827/) | `IC ngô͘-it-sù-lio̍k` | `ngô͘` |
| [20220908](https://apod.tw/daily/20220908/) | `Thê-ô͘-seng-hûn` | `ô͘` |
| [20220908](https://apod.tw/daily/20220908/) | `sàng-sò͘` | `sò͘` |
| [20220921](https://apod.tw/daily/20220921/) | `seng-chè-thô͘-hún-hûn` | `chè`, `thô͘` |
| [20220921](https://apod.tw/daily/20220921/) | `La̍h-hō͘-chō Sigma` | `hō͘`, `chō` |
| [20220929](https://apod.tw/daily/20220929/) | `Khin-hîng I-tà-lī Sió-kiânn-tshinn Sîng-siōng Li̍p-hong-Uē-tshnn` | `tshnn` |
| [20221001](https://apod.tw/daily/20221001/) | `goe̍h-îⁿ` | `îⁿ` |
| [20221006](https://apod.tw/daily/20221006/) | `seng-hē-phōaⁿ` | `phōaⁿ` |
| [20221009](https://apod.tw/daily/20221009/) | `lia̍p-chú` | `chú` |
| [20221102](https://apod.tw/daily/20221102/) | `ji̍t-jíⁿ` | `jíⁿ` |
| [20221105](https://apod.tw/daily/20221105/) | `BICEP Bōng-oán-kiàⁿ` | `kiàⁿ` |
| [20221107](https://apod.tw/daily/20221107/) | `Kok-chè Ōaⁿ-ji̍t-sòaⁿ` | `chè`, `Ōaⁿ`, `sòaⁿ` |
| [20221112](https://apod.tw/daily/20221112/) | `goe̍h-choân-si̍t` | `choân` |
| [20221118](https://apod.tw/daily/20221118/) | `guân-hîng-tshinn puânnd` | `puânnd` |
| [20221121](https://apod.tw/daily/20221121/) | `chí-gōa-kng` | `chí` |
| [20221230](https://apod.tw/daily/20221230/) | `sī-sòaⁿMessier sì-tsa̍p-gōo` | `sòaⁿMessier` |
| [20230118](https://apod.tw/daily/20230118/) | `James Webb Thài-khong bōng-oán-kiàⁿ` | `kiàⁿ` |
| [20230202](https://apod.tw/daily/20230202/) | `guân-chú` | `chú` |
| [20230425](https://apod.tw/daily/20230425/) | `chit-chú` | `chú` |
| [20230503](https://apod.tw/daily/20230503/) | `Sū-kiāⁿ-sī-kài Bōng-oán-kiàⁿ` | `kiāⁿ`, `kiàⁿ` |
| [20230505](https://apod.tw/daily/20230505/) | `bín-kám-tō͘` | `tō͘` |
| [20230622](https://apod.tw/daily/20230622/) | `hun-chú-hûn hok-ha̍p-thé` | `chú` |
| [20230629](https://apod.tw/daily/20230629/) | `tiōng-li̍k-photiōng-li̍k-pho` | `photiōng` |
| [20231009](https://apod.tw/daily/20231009/) | `lji̍t-tsuân-si̍t` | `lji̍t` |
| [20231020](https://apod.tw/daily/20231020/) | `NGC sù-jī-ngó͘-pat` | `ngó͘` |
| [20231026](https://apod.tw/daily/20231026/) | `thô͘-hún-lia̍p` | `thô͘` |
| [20231110](https://apod.tw/daily/20231110/) | `hoat-siā-sòaⁿ` | `sòaⁿ` |
| [20231112](https://apod.tw/daily/20231112/) | `gue̍h-îⁿ` | `îⁿ` |
| [20231127](https://apod.tw/daily/20231127/) | `hun-chú-hûn` | `chú` |
| [20231212](https://apod.tw/daily/20231212/) | `Sian-lú-chō Seng-hē` | `chō` |
First 50 of 74 rows; the JSON report lists them all.

### Words with more than one tone mark (input form not built)

0 rows.

### Cells with a caron on a tone-bearing letter

1 rows.

| Where | Text |
|---|---|
| [20250401](https://apod.tw/daily/20250401/) row 4 KipUnicode | `tē-pîng-sǔn` |

## 4. Counts

| Count | Value |
|---|---|
| `articles_sitemap` | 1,511 |
| `articles_listing` | 1,511 |
| `listing_pages` | 7 |
| `articles` | 1,511 |
| `articles_fetched` | 1,511 |
| `articles_missing` | 0 |
| `articles_with_table` | 1,511 |
| `tables_expected_headers` | 1,511 |
| `articles_titles_incomplete` | 7 |
| `rows` | 13,587 |
| `rows_distinct_poj` | 4,943 |
| `rows_distinct_hanlo` | 4,091 |
| `rows_PojUnicode` | 13,581 |
| `rows_PojInput` | 13,581 |
| `rows_KipUnicode` | 13,575 |
| `rows_KipInput` | 13,575 |
| `rows_HanLoTaibunPoj` | 13,587 |
| `rows_HoaBun` | 13,582 |
| `rows_EngBun` | 13,578 |
| `rows_LaigoanMia` | 13,587 |
| `rows_LaigoanBangchi` | 13,587 |
| `rows_empty_cells` | 29 |
| `rows_not_poj` | 9 |
| `rows_not_kpl` | 74 |
| `rows_caron` | 1 |
| `articles_rows` | 1,511 |
| `articles_no_heading` | 0 |
| `articles_no_table` | 0 |
| `articles_empty_table` | 0 |
| `articles_multi_tone` | 0 |
| `rows_multi_tone` | 0 |
| `rows_blank_skipped` | 0 |
| `tables_other_headers` | 0 |
| `rows_cell_count_mismatch` | 0 |
