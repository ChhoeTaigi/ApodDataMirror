# ApodDataQuality

Version `20261020-000554`, built from https://apod.tw/ (articles 20190411 to 20251004).

## 1. Articles

- 1,511 daily articles in `sitemap.xml`
- 1,511 on the 7 pages of the `/daily/` listing
- 1,511 in their union, 1,511 fetched, 0 answering 404
- 1,511 with a 詞彙學習 table, 0 with no 詞彙學習 heading, 0 with the heading but no table
- 0 with a table of no rows

### Titles

Every article's title is read from its `[漢羅]`, `[POJ]`, `[KIP]` and `[English]` headings and is its first row in `ApodSului` (`WordId` ending in `-00`; `HoaBun` empty, the site has no Mandarin title). Articles lacking one or more headings (an empty heading counts as lacking): 7. One lacking all four and the `<h1>` would get no title row.

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
- 0 rows after the header are written in header cells (kept as rows)

## 3. Rows

15,098 rows in `ApodSului`: 1,511 titles (one per article, `WordId` ending in `-00`) and 13,587 table rows, with 4,943 distinct `PojUnicode` and 4,091 distinct `HanLoTaibunPoj` among the table rows.

| Column | Rows filled |
|---|---|
| `WordId` | 15,098 |
| `PojUnicode` | 15,090 |
| `PojInput` | 15,090 |
| `KipUnicode` | 15,083 |
| `KipInput` | 15,083 |
| `HanLoTaibunPoj` | 15,098 |
| `HoaBun` | 13,582 |
| `EngBun` | 15,088 |
| `LaigoanMia` | 15,098 |
| `LaigoanBangchi` | 15,098 |

### Table rows with an empty cell (a title row lacking a heading is listed under Titles)

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

17 rows.

| Where | Cell | Pieces |
|---|---|---|
| [20210829](https://apod.tw/daily/20210829/) row 3 | `Siang Sió-kiânn-tshinn Tiông-sin-tīng-hiòng Tshik-giām` | `kiânn` |
| [20211214](https://apod.tw/daily/20211214/) row 7 | `HH lio̍k-lio̍k柱-lio̍k thian-thé` | `lio̍k柱` |
| [20221017](https://apod.tw/daily/20221017/) row 3 | `hok-siā-suànn` | `suànn` |
| [20230408](https://apod.tw/daily/20230408/) title | `M100: Tsi̍t-ê Uí-tāi-siat-kè ê Kńg-lê-á Sing-hē` | `Tsi̍t` |
| [20230530](https://apod.tw/daily/20230530/) title | `Ḿ7: É-cheng seng-hûn` | `Ḿ7` |
| [20230603](https://apod.tw/daily/20230603/) row 9 | `hū-phìnn` | `phìnn` |
| [20230831](https://apod.tw/daily/20230831/) title | `Tsài-lâng 7 hō Jīm-bū ê Sing-hûn` | `Tsài` |
| [20231104](https://apod.tw/daily/20231104/) title | `Dinkinesh Sió-kiânn-tshenn ê Gue̍h-tshut` | `kiânn` |
| [20231110](https://apod.tw/daily/20231110/) row 5 | `Gio̍k-hu-tsō` | `tsō` |
| [20240524](https://apod.tw/daily/20240524/) title | `Euclid Thài-khong Bōng-oán-kiàⁿ hip--tio̍h ê Hêng-chheⁿ hêng-sêng-khu M̄8` | `M̄8` |
| [20240916](https://apod.tw/daily/20240916/) title | `BepiColombo Thài-khong-tsûn hip--ê Tsuí-tshenn ún-si̍k-khenn Vivaldi` | `tsûn`, `Tsuí` |
| [20241107](https://apod.tw/daily/20241107/) title | `Siang-hî-tsō lāi-té ê Hûn-khak Sing-hē` | `tsō` |
| [20250721](https://apod.tw/daily/20250721/) row 6 | `Uí-peh Thài-khong Bōng-uán-kiànn` | `kiànn` |
| [20250721](https://apod.tw/daily/20250721/) row 8 | `hun-tsú hûn` | `tsú` |
| [20250908](https://apod.tw/daily/20250908/) title | `IRAS 04302: Hô͘-tia̍p-pôaⁿ ê Hhêng-chhiⁿ Hêng-sêng` | `Hhêng` |
| [20250922](https://apod.tw/daily/20250922/) row 6 | `pak-puànn-kiû` | `puànn` |
| [20250922](https://apod.tw/daily/20250922/) row 7 | `lâm-puànn-kiû` | `puànn` |

### KIP cells with a piece that is not KPL

94 rows.

| Where | Cell | Pieces |
|---|---|---|
| [20210117](https://apod.tw/daily/20210117/) row 4 | `tiān-chiunn phùn-lâu` | `chiunn` |
| [20210210](https://apod.tw/daily/20210210/) row 10 | `sī-bāng-mo̍͘h` | `mo̍͘h` |
| [20210211](https://apod.tw/daily/20210211/) row 1 | `Thian-gô-chō` | `chō` |
| [20210311](https://apod.tw/daily/20210311/) row 8 | `sing-tsè-thô͘-hún-lia̍p` | `thô͘` |
| [20210312](https://apod.tw/daily/20210312/) title | `Messier pueh-cha̍p-it` | `cha̍p` |
| [20210314](https://apod.tw/daily/20210314/) title | `Messier pueh-cha̍p-it` | `cha̍p` |
| [20210318](https://apod.tw/daily/20210318/) title | `Ing-sian-tsō hun-chú-hûn ê sing-tsè thô͘-hún` | `chú`, `thô͘` |
| [20210412](https://apod.tw/daily/20210412/) title | `Tsham-siùg-it kah Hué-tsi̍h sing-hûn` | `siùg` |
| [20210423](https://apod.tw/daily/20210423/) row 1 | `Kok-chè-thài-khong-chām` | `chè`, `chām` |
| [20210512](https://apod.tw/daily/20210512/) row 4 | `kiânn-tshinn-kan thô͘-hún-lia̍p` | `thô͘` |
| [20210524](https://apod.tw/daily/20210524/) row 1 | `iûnn-á kiânn-tshiⁿ` | `tshiⁿ` |
| [20210606](https://apod.tw/daily/20210606/) row 7 | `lji̍t-tsuân-si̍t` | `lji̍t` |
| [20210609](https://apod.tw/daily/20210609/) row 4 | `Tshiau-kip hue-hueh-gue̍he` | `gue̍he` |
| [20210620](https://apod.tw/daily/20210620/) title | `Tī Stonehenge thinn-tíng ê ji̍t-tshut hā-chì` | `chì` |
| [20210718](https://apod.tw/daily/20210718/) row 4 | `tn̂g-tu-îⁿ sing-hē` | `îⁿ` |
| [20210721](https://apod.tw/daily/20210721/) row 4 | `sng-sò͘` | `sò͘` |
| [20210817](https://apod.tw/daily/20210817/) title | `M-gō͘-cha̍p-chhit: Hap-peh hip--ê Khoân-hêng-seng-hûn` | `gō͘`, `cha̍p` |
| [20210820](https://apod.tw/daily/20210820/) title | `Saⁿ-àm ê Eng-sian-chō liû-chhiⁿ` | `chō` |
| [20210902](https://apod.tw/daily/20210902/) title | `M̂1: O-lûn sing-hē` | `M̂1` |
| [20211006](https://apod.tw/daily/20211006/) row 5 | `Chhiâ-ko-hîng sing-thuân` | `Chhiâ` |
| [20211006](https://apod.tw/daily/20211006/) row 6 | `Chhiâ-to-hîng sing-thuân` | `Chhiâ` |
| [20211205](https://apod.tw/daily/20211205/) title | `Tī Sè-kài kha-chhng-bóe ê Ji̍t-choân-si̍t` | `choân` |
| [20220129](https://apod.tw/daily/20220129/) title | `Thian-lô͘-chō seng-hē-thoân` | `lô͘`, `chō` |
| [20220602](https://apod.tw/daily/20220602/) row 8 | `thàu-chá-chhiⁿ` | `chá` |
| [20220610](https://apod.tw/daily/20220610/) row 2 | `Sik-lú-chō` | `chō` |
| [20220613](https://apod.tw/daily/20220613/) title | `M̂1: Hubble Thài-khong-bōng-uán-kiànn hip--ê O-lûn-sing-hē` | `M̂1` |
| [20220614](https://apod.tw/daily/20220614/) row 2 | `kē kuí-tō se̍h-tē-uī-chhiⁿâ` | `chhiⁿâ` |
| [20220708](https://apod.tw/daily/20220708/) row 2 | `hî-gán-kiàⁿ-thâu` | `kiàⁿ` |
| [20220722](https://apod.tw/daily/20220722/) title | `Kńg-lê-á sing-hē M̄4: Khah tshing-tshóo ê pán-pún` | `M̄4` |
| [20220723](https://apod.tw/daily/20220723/) row 6 | `Lêng-chēng-hái` | `chēng` |
| [20220814](https://apod.tw/daily/20220814/) row 8 | `bî-tiōng-le̍k thàu-kiàⁿ-hāu-èng` | `kiàⁿ` |
| [20220816](https://apod.tw/daily/20220816/) row 5 | `Ing-sian-tsō liû-tshinn-hō͘lta Lâm Liû-tshinn-hōo` | `hō͘lta` |
| [20220827](https://apod.tw/daily/20220827/) row 1 | `IC ngô͘-it-sù-lio̍k` | `ngô͘` |
| [20220902](https://apod.tw/daily/20220902/) title | `M̂1: O-lûn-sing-hē` | `M̂1` |
| [20220908](https://apod.tw/daily/20220908/) row 2 | `Thê-ô͘-seng-hûn` | `ô͘` |
| [20220908](https://apod.tw/daily/20220908/) row 5 | `sàng-sò͘` | `sò͘` |
| [20220913](https://apod.tw/daily/20220913/) title | `Thài-iông bīn-téng ê Tn̂g-chôa-hêng Thài-iông-si` | `chôa` |
| [20220921](https://apod.tw/daily/20220921/) row 3 | `seng-chè-thô͘-hún-hûn` | `chè`, `thô͘` |
| [20220921](https://apod.tw/daily/20220921/) row 7 | `La̍h-hō͘-chō Sigma` | `hō͘`, `chō` |
| [20220929](https://apod.tw/daily/20220929/) row 3 | `Khin-hîng I-tà-lī Sió-kiânn-tshinn Sîng-siōng Li̍p-hong-Uē-tshnn` | `tshnn` |
| [20221001](https://apod.tw/daily/20221001/) row 5 | `goe̍h-îⁿ` | `îⁿ` |
| [20221006](https://apod.tw/daily/20221006/) row 7 | `seng-hē-phōaⁿ` | `phōaⁿ` |
| [20221009](https://apod.tw/daily/20221009/) row 4 | `lia̍p-chú` | `chú` |
| [20221102](https://apod.tw/daily/20221102/) row 3 | `ji̍t-jíⁿ` | `jíⁿ` |
| [20221103](https://apod.tw/daily/20221103/) title | `M̀3: Sann-kak-tsō sing-hē` | `M̀3` |
| [20221105](https://apod.tw/daily/20221105/) row 12 | `BICEP Bōng-oán-kiàⁿ` | `kiàⁿ` |
| [20221107](https://apod.tw/daily/20221107/) row 10 | `Kok-chè Ōaⁿ-ji̍t-sòaⁿ` | `chè`, `Ōaⁿ`, `sòaⁿ` |
| [20221112](https://apod.tw/daily/20221112/) row 1 | `goe̍h-choân-si̍t` | `choân` |
| [20221118](https://apod.tw/daily/20221118/) row 4 | `guân-hîng-tshinn puânnd` | `puânnd` |
| [20221121](https://apod.tw/daily/20221121/) row 5 | `chí-gōa-kng` | `chí` |
First 50 of 94 rows; the JSON report lists them all.

### Words with more than one tone mark (input form not built)

0 rows.

### Cells with a caron on a tone-bearing letter

4 rows.

| Where | Text |
|---|---|
| [20230519](https://apod.tw/daily/20230519/) title KipUnicode | `Khiû-môo ê Kńg-lê-á Sing-hē M̌3` |
| [20250401](https://apod.tw/daily/20250401/) row 4 KipUnicode | `tē-pîng-sǔn` |
| [20250522](https://apod.tw/daily/20250522/) title KipUnicode | `Khiû-môo ê Kńg-lê-á Sing-hē M̌3` |
| [20250624](https://apod.tw/daily/20250624/) title PojUnicode | `Kńg-lê-á Seng-hē M̌1 ê tiong-sim` |

## 4. Counts

| Count | Value |
|---|---|
| `articles_sitemap` | 1,511 |
| `articles_listing` | 1,511 |
| `listing_pages` | 7 |
| `articles` | 1,511 |
| `articles_fetched` | 1,511 |
| `articles_missing` | 0 |
| `rows_title` | 1,511 |
| `articles_with_table` | 1,511 |
| `tables_expected_headers` | 1,511 |
| `rows_table` | 13,587 |
| `articles_titles_incomplete` | 7 |
| `rows` | 15,098 |
| `rows_distinct_poj` | 4,943 |
| `rows_distinct_hanlo` | 4,091 |
| `rows_WordId` | 15,098 |
| `rows_PojUnicode` | 15,090 |
| `rows_PojInput` | 15,090 |
| `rows_KipUnicode` | 15,083 |
| `rows_KipInput` | 15,083 |
| `rows_HanLoTaibunPoj` | 15,098 |
| `rows_HoaBun` | 13,582 |
| `rows_EngBun` | 15,088 |
| `rows_LaigoanMia` | 15,098 |
| `rows_LaigoanBangchi` | 15,098 |
| `rows_empty_cells` | 29 |
| `rows_not_poj` | 17 |
| `rows_not_kpl` | 94 |
| `rows_caron` | 4 |
| `articles_no_heading` | 0 |
| `articles_no_table` | 0 |
| `articles_empty_table` | 0 |
| `rows_multi_tone` | 0 |
| `rows_blank_skipped` | 0 |
| `tables_other_headers` | 0 |
| `rows_cell_count_mismatch` | 0 |
| `rows_header_like` | 0 |
