# Extracted bootstrap and opt-dist intervals

Log markers, not inferred pure compilation. Tiny bootstrap dry-run groups are retained.
Nested intervals must not be summed. Exclusive categories are in `summary.json`.

## [auto - dist-aarch64-linux: 100999914865](https://github.com/rust-lang/rust/actions/runs/33865610474/job/100999914865)

Run 33865610474; raw SHA256 `32cad4520718b99f0d686a740098e4980f1142bbb13c0a482bc4d6042b1583e6`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 3.137 |
| Build support | 1.462 |
| LLVM/LLD | 14.190 |
| Compiler | 9.924 |
| Tools | 23.931 |
| Libraries | 0.462 |
| Tests | 8.028 |
| Docs | 4.154 |
| Packaging | 4.397 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-04T11:00:06.9942023Z | 2026-09-04T11:00:06.9959650Z | Run set +e | 0.000 | 1443 |
| 2026-09-04T11:00:07.0295393Z | 2026-09-04T11:00:07.0378442Z | Image checksum input | 0.000 | 1484 |
| 2026-09-04T11:00:07.0379548Z | 2026-09-04T11:00:30.5743167Z | Building docker image for dist-aarch64-linux | 0.392 | 1903 |
| 2026-09-04T11:00:33.2032514Z | 2026-09-04T11:00:33.2236828Z | Clock drift check | 0.000 | 1980 |
| 2026-09-04T11:00:33.5375135Z | 2026-09-04T11:00:33.5391878Z | Configure the build | 0.000 | 1986 |
| 2026-09-04T11:00:41.9305324Z | 2026-09-04T11:00:51.9148724Z | Building bootstrap | 0.166 | 2041 |
| 2026-09-04T11:00:52.0995274Z | 2026-09-04T11:00:52.0996543Z | Building LLVM for aarch64-unknown-linux-gnu | 0.000 | 2172 |
| 2026-09-04T11:00:52.0998261Z | 2026-09-04T11:00:52.0999083Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2174 |
| 2026-09-04T11:00:52.1000182Z | 2026-09-04T11:00:52.1000617Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2177 |
| 2026-09-04T11:00:52.1001733Z | 2026-09-04T11:00:52.1002119Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2179 |
| 2026-09-04T11:00:52.1003552Z | 2026-09-04T11:00:52.1003941Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2181 |
| 2026-09-04T11:00:52.1004933Z | 2026-09-04T11:00:52.1005384Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2183 |
| 2026-09-04T11:00:52.1007111Z | 2026-09-04T11:00:52.1007509Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2185 |
| 2026-09-04T11:00:52.1008642Z | 2026-09-04T11:00:52.1009089Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2187 |
| 2026-09-04T11:00:52.1010134Z | 2026-09-04T11:00:52.1010541Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2190 |
| 2026-09-04T11:00:52.1011317Z | 2026-09-04T11:00:52.1011702Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2192 |
| 2026-09-04T11:00:52.1013219Z | 2026-09-04T11:00:52.1013606Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2194 |
| 2026-09-04T11:00:52.1014377Z | 2026-09-04T11:00:52.1014770Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2196 |
| 2026-09-04T11:00:52.1017791Z | 2026-09-04T11:00:52.1018223Z | Building stage2 cargo (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2199 |
| 2026-09-04T11:00:52.1019442Z | 2026-09-04T11:00:52.1019824Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2201 |
| 2026-09-04T11:00:52.1021184Z | 2026-09-04T11:00:52.1021622Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2203 |
| 2026-09-04T11:00:52.1022629Z | 2026-09-04T11:00:52.1023177Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2205 |
| 2026-09-04T11:00:52.1024014Z | 2026-09-04T11:00:52.1031296Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2207 |
| 2026-09-04T11:00:52.1031635Z | 2026-09-04T11:00:52.1032021Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2209 |
| 2026-09-04T11:00:52.1032334Z | 2026-09-04T11:00:52.1032689Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2211 |
| 2026-09-04T11:00:52.1032999Z | 2026-09-04T11:00:52.1033361Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2213 |
| 2026-09-04T11:00:52.1033665Z | 2026-09-04T11:00:52.1034014Z | Building stage2 miri (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2215 |
| 2026-09-04T11:00:52.1034335Z | 2026-09-04T11:00:52.1034699Z | Building stage2 cargo-miri (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2217 |
| 2026-09-04T11:00:52.1115165Z | 2026-09-04T11:00:52.1173285Z | Display CPU and Memory information | 0.000 | 2220 |
| 2026-09-04T11:00:52.1693407Z | 2026-09-04T11:00:52.2050561Z | Building bootstrap | 0.001 | 2423 |
| 2026-09-04T11:00:52.3973565Z | 2026-09-04T11:01:05.8067875Z | Building stage1 opt-dist (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.223 | 2436 |
| 2026-09-04T11:01:05.8162668Z | 2026-09-04T11:01:05.8180698Z | Environment values | 0.000 | 2660 |
| 2026-09-04T11:01:05.8180947Z | 2026-09-04T11:01:05.8237264Z | Printing bootstrap.toml | 0.000 | 2714 |
| 2026-09-04T11:01:05.8238055Z | 2026-09-04T11:01:28.0287291Z | Building rustc-perf | 0.370 | 2949 |
| 2026-09-04T11:01:28.0822279Z | 2026-09-04T11:01:28.1199997Z | Building bootstrap | 0.001 | 3485 |
| 2026-09-04T11:01:28.3285748Z | 2026-09-04T11:02:43.6587641Z | Building LLVM for aarch64-unknown-linux-gnu | 1.256 | 3496 |
| 2026-09-04T11:02:43.6708501Z | 2026-09-04T11:07:03.5159064Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-unknown-linux-gnu) | 4.331 | 11069 |
| 2026-09-04T11:07:03.7017192Z | 2026-09-04T11:08:24.9395506Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-unknown-linux-gnu) | 1.354 | 11760 |
| 2026-09-04T11:08:24.9399494Z | 2026-09-04T11:08:28.0588815Z | Building LLD for aarch64-unknown-linux-gnu | 0.052 | 11879 |
| 2026-09-04T11:08:28.0592093Z | 2026-09-04T11:08:28.3144596Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.004 | 12151 |
| 2026-09-04T11:08:28.3150133Z | 2026-09-04T11:08:47.5377202Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.320 | 12160 |
| 2026-09-04T11:08:47.5382999Z | 2026-09-04T11:08:50.9894895Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.058 | 12299 |
| 2026-09-04T11:08:51.1352919Z | 2026-09-04T11:09:00.0799588Z | Building sanitizers for aarch64-unknown-linux-gnu | 0.149 | 12372 |
| 2026-09-04T11:09:00.0804270Z | 2026-09-04T11:09:27.4908464Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-unknown-linux-gnu) | 0.457 | 13131 |
| 2026-09-04T11:09:27.4970305Z | 2026-09-04T11:12:02.2768710Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-unknown-linux-gnu) | 2.580 | 13207 |
| 2026-09-04T11:12:02.2819306Z | 2026-09-04T11:13:48.3381208Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-unknown-linux-gnu) | 1.768 | 13799 |
| 2026-09-04T11:13:48.3386286Z | 2026-09-04T11:13:48.6544642Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.005 | 13893 |
| 2026-09-04T11:13:48.6551418Z | 2026-09-04T11:14:13.0915584Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.407 | 13902 |
| 2026-09-04T11:14:13.0921002Z | 2026-09-04T11:14:17.3705994Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.071 | 14029 |
| 2026-09-04T11:14:17.3723732Z | 2026-09-04T11:15:55.4509837Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-unknown-linux-gnu) | 1.635 | 14103 |
| 2026-09-04T11:15:55.4515416Z | 2026-09-04T11:20:04.6728177Z | Building stage2 cargo (stage1 -> stage2, aarch64-unknown-linux-gnu) | 4.154 | 14302 |
| 2026-09-04T11:20:04.6734474Z | 2026-09-04T11:22:03.7908347Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-unknown-linux-gnu) | 1.985 | 15191 |
| 2026-09-04T11:22:03.7914806Z | 2026-09-04T11:22:03.9116872Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 15375 |
| 2026-09-04T11:22:03.9254610Z | 2026-09-04T11:25:43.7522486Z | Running benchmarks | 3.664 | 15529 |
| 2026-09-04T11:26:46.3168907Z | 2026-09-04T11:27:09.6243975Z | Running benchmarks | 0.388 | 15603 |
| 2026-09-04T11:27:17.0662381Z | 2026-09-04T11:27:58.7576061Z | Running benchmarks | 0.695 | 15656 |
| 2026-09-04T11:28:07.4749987Z | 2026-09-04T11:28:07.8188300Z | Building bootstrap | 0.006 | 15712 |
| 2026-09-04T11:28:08.7630201Z | 2026-09-04T11:28:10.7952521Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.034 | 15738 |
| 2026-09-04T11:28:10.9852386Z | 2026-09-04T11:28:11.3302467Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.006 | 16060 |
| 2026-09-04T11:28:11.3311955Z | 2026-09-04T11:28:11.4094956Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.001 | 16117 |
| 2026-09-04T11:28:11.4105336Z | 2026-09-04T11:28:11.8167462Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.007 | 16125 |
| 2026-09-04T11:28:11.8172926Z | 2026-09-04T11:28:11.9817590Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.003 | 16197 |
| 2026-09-04T11:28:12.2165978Z | 2026-09-04T11:28:12.5259718Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-unknown-linux-gnu) | 0.005 | 16249 |
| 2026-09-04T11:28:12.5318531Z | 2026-09-04T11:31:11.3048781Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-unknown-linux-gnu) | 2.980 | 16291 |
| 2026-09-04T11:31:11.5043312Z | 2026-09-04T11:31:25.8986858Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.240 | 16851 |
| 2026-09-04T11:31:25.8991332Z | 2026-09-04T11:31:25.9805622Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.001 | 16907 |
| 2026-09-04T11:31:25.9811121Z | 2026-09-04T11:31:26.3647581Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.006 | 16915 |
| 2026-09-04T11:31:26.3652935Z | 2026-09-04T11:31:26.5180051Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.003 | 16987 |
| 2026-09-04T11:31:26.5196594Z | 2026-09-04T11:32:44.7340534Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-unknown-linux-gnu) | 1.304 | 17042 |
| 2026-09-04T11:32:44.7351405Z | 2026-09-04T11:35:54.6864326Z | Building stage2 cargo (stage1 -> stage2, aarch64-unknown-linux-gnu) | 3.166 | 17210 |
| 2026-09-04T11:35:54.6871571Z | 2026-09-04T11:37:32.6598200Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-unknown-linux-gnu) | 1.633 | 17918 |
| 2026-09-04T11:37:32.6604269Z | 2026-09-04T11:37:32.7928532Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 18088 |
| 2026-09-04T11:37:34.0378950Z | 2026-09-04T11:37:34.0984049Z | Building bootstrap | 0.001 | 18247 |
| 2026-09-04T11:37:34.2845189Z | 2026-09-04T11:41:03.2081556Z | Building LLVM for aarch64-unknown-linux-gnu | 3.482 | 18258 |
| 2026-09-04T11:41:03.2198589Z | 2026-09-04T11:41:10.4575397Z | Building LLD for aarch64-unknown-linux-gnu | 0.121 | 25846 |
| 2026-09-04T11:41:10.4578453Z | 2026-09-04T11:41:10.5298931Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.001 | 26122 |
| 2026-09-04T11:41:10.5304241Z | 2026-09-04T11:41:10.6335674Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.002 | 26130 |
| 2026-09-04T11:41:10.6341238Z | 2026-09-04T11:41:10.7257062Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.002 | 26202 |
| 2026-09-04T11:41:10.8793565Z | 2026-09-04T11:41:10.9520853Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.001 | 26269 |
| 2026-09-04T11:41:10.9526228Z | 2026-09-04T11:41:11.0412158Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.001 | 26277 |
| 2026-09-04T11:41:11.0417391Z | 2026-09-04T11:41:11.1244562Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.001 | 26349 |
| 2026-09-04T11:41:11.1373958Z | 2026-09-04T11:43:08.2056434Z | Running benchmarks | 1.951 | 26448 |
| 2026-09-04T11:43:45.0531090Z | 2026-09-04T11:43:45.3556226Z | Building bootstrap | 0.005 | 26506 |
| 2026-09-04T11:43:45.9131272Z | 2026-09-04T11:52:55.5339794Z | Building LLVM for aarch64-unknown-linux-gnu | 9.160 | 26518 |
| 2026-09-04T11:52:55.9922113Z | 2026-09-04T11:53:03.1445597Z | Building LLD for aarch64-unknown-linux-gnu | 0.119 | 34101 |
| 2026-09-04T11:53:03.1449117Z | 2026-09-04T11:53:03.3174795Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.003 | 34377 |
| 2026-09-04T11:53:03.3179931Z | 2026-09-04T11:53:03.6145995Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.005 | 34385 |
| 2026-09-04T11:53:03.6151622Z | 2026-09-04T11:53:03.7583149Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.002 | 34457 |
| 2026-09-04T11:53:03.9564767Z | 2026-09-04T11:53:16.6840797Z | Building stage1 unstable-book-gen (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.212 | 34517 |
| 2026-09-04T11:53:19.1046000Z | 2026-09-04T11:53:36.5846410Z | Building stage1 rustbook (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.291 | 34749 |
| 2026-09-04T11:53:41.2220937Z | 2026-09-04T11:53:41.2244387Z | Documenting stage2 book redirect pages (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 35176 |
| 2026-09-04T11:53:41.2244827Z | 2026-09-04T11:54:44.2070054Z | Building stage1 rustdoc-tool-binary (stage0 -> stage1, aarch64-unknown-linux-gnu) | 1.050 | 35180 |
| 2026-09-04T11:54:44.2070473Z | 2026-09-04T11:54:44.8198481Z | Documenting stage2 book redirect pages (stage1 -> stage2, aarch64-unknown-linux-gnu) (continued) | 0.010 | 35365 |
| 2026-09-04T11:54:44.8200518Z | 2026-09-04T11:54:45.0502639Z | Documenting stage2 standalone (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.004 | 35371 |
| 2026-09-04T11:54:45.0507299Z | 2026-09-04T11:55:01.1437114Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage1 -> stage1, aarch64-unknown-linux-gnu) | 0.268 | 35375 |
| 2026-09-04T11:55:01.1461995Z | 2026-09-04T11:55:43.9575346Z | Documenting stage2 compiler{rustc-main, rustc_abi, rustc_arena, rustc_ast, rustc_ast_ir, rustc_ast_lowering, rustc_ast_passes, rustc_ast_pretty, rustc_attr_ir, rustc_attr_parsing, rustc_baked_icu_data, rustc_borrowck, rustc_builtin_macros, rustc_codegen_llvm, rustc_codegen_ssa, rustc_const_eval, rustc_crate_store, rustc_data_structures, rustc_driver, rustc_driver_impl, rustc_error_codes, rustc_error_messages, rustc_errors, rustc_expand, rustc_feature, rustc_fs_util, rustc_graphviz, rustc_hashes, rustc_hir, rustc_hir_analysis, rustc_hir_id, rustc_hir_pretty, rustc_hir_typeck, rustc_incremental, rustc_index, rustc_index_macros, rustc_infer, rustc_interface, rustc_lexer, rustc_lint, rustc_lint_defs, rustc_llvm, rustc_log, rustc_macros, rustc_metadata, rustc_middle, rustc_mir_build, rustc_mir_dataflow, rustc_mir_transform, rustc_monomorphize, rustc_next_trait_solver, rustc_parse, rustc_parse_format, rustc_passes, rustc_pattern_analysis, rustc_privacy, rustc_proc_macro, rustc_public, rustc_public_bridge, rustc_query_impl, rustc_resolve, rustc_sanitizers, rustc_serialize, rustc_session, rustc_span, rustc_structures, rustc_symbol_mangling, rustc_target, rustc_thread_pool, rustc_trait_selection, rustc_traits, rustc_transmute, rustc_ty_utils, rustc_ty_walk, rustc_type_ir, rustc_type_ir_macros, rustc_windows_rc} (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.714 | 35444 |
| 2026-09-04T11:55:44.1629587Z | 2026-09-04T11:55:44.2405960Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.001 | 36123 |
| 2026-09-04T11:55:44.2411412Z | 2026-09-04T11:55:44.5572172Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.005 | 36131 |
| 2026-09-04T11:55:44.5577565Z | 2026-09-04T11:55:44.7034591Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 36203 |
| 2026-09-04T11:55:44.7045183Z | 2026-09-04T11:55:55.5396598Z | Documenting stage2 rustdoc (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.181 | 36250 |
| 2026-09-04T11:55:55.5404888Z | 2026-09-04T11:56:03.1228015Z | Documenting stage2 rustfmt (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.126 | 36439 |
| 2026-09-04T11:56:03.1233882Z | 2026-09-04T11:56:15.1625454Z | Building stage2 error_index_generator (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.201 | 36624 |
| 2026-09-04T11:56:37.9137678Z | 2026-09-04T11:56:40.5719840Z | Building stage1 lint-docs (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.044 | 36961 |
| 2026-09-04T11:56:40.5767166Z | 2026-09-04T11:56:53.4835981Z | Running stage2 lint-docs (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.215 | 36995 |
| 2026-09-04T11:56:53.9725462Z | 2026-09-04T11:57:38.4288444Z | Documenting stage2 cargo (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.741 | 37008 |
| 2026-09-04T11:57:38.8556190Z | 2026-09-04T11:57:41.7981920Z | Documenting stage2 clippy (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.049 | 37836 |
| 2026-09-04T11:57:41.9214188Z | 2026-09-04T11:57:41.9236509Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 37879 |
| 2026-09-04T11:57:41.9236838Z | 2026-09-04T11:57:59.5670007Z | Documenting stage2 miri (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.294 | 37882 |
| 2026-09-04T11:57:59.5670464Z | 2026-09-04T11:57:59.5672830Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, aarch64-unknown-linux-gnu) (continued) | 0.000 | 38046 |
| 2026-09-04T11:57:59.5673158Z | 2026-09-04T11:58:05.7713112Z | Documenting stage2 tidy (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.103 | 38050 |
| 2026-09-04T11:58:05.7713637Z | 2026-09-04T11:58:05.7716020Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, aarch64-unknown-linux-gnu) (continued) | 0.000 | 38267 |
| 2026-09-04T11:58:05.7716362Z | 2026-09-04T11:58:15.5135855Z | Documenting stage2 bootstrap (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.162 | 38271 |
| 2026-09-04T11:58:15.5136293Z | 2026-09-04T11:58:15.5138872Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, aarch64-unknown-linux-gnu) (continued) | 0.000 | 38436 |
| 2026-09-04T11:58:15.5139263Z | 2026-09-04T11:58:16.3362561Z | Documenting stage2 buildhelper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.014 | 38440 |
| 2026-09-04T11:58:16.3362971Z | 2026-09-04T11:58:16.3365235Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, aarch64-unknown-linux-gnu) (continued) | 0.000 | 38447 |
| 2026-09-04T11:58:16.3365577Z | 2026-09-04T11:58:20.7852754Z | Documenting stage2 compiletest (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.074 | 38451 |
| 2026-09-04T11:58:20.7853204Z | 2026-09-04T11:58:20.7855827Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, aarch64-unknown-linux-gnu) (continued) | 0.000 | 38593 |
| 2026-09-04T11:58:20.7856176Z | 2026-09-04T11:58:25.2727435Z | Documenting stage2 runmakesupport (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.075 | 38597 |
| 2026-09-04T11:58:25.2727850Z | 2026-09-04T11:58:28.3582772Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, aarch64-unknown-linux-gnu) (continued) | 0.051 | 38680 |
| 2026-09-04T11:58:28.6809096Z | 2026-09-04T11:58:28.7412562Z | Documenting stage2 releases (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.001 | 38713 |
| 2026-09-04T11:58:29.3613800Z | 2026-09-04T11:58:40.9326025Z | Building stage1 rust-installer (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.193 | 38718 |
| 2026-09-04T11:59:33.8447704Z | 2026-09-04T11:59:40.3078885Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage1 -> stage1, aarch64-unknown-linux-gnu) | 0.108 | 38806 |
| 2026-09-04T11:59:44.4035829Z | 2026-09-04T11:59:44.7591392Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.006 | 38856 |
| 2026-09-04T11:59:44.7598516Z | 2026-09-04T12:00:02.0975856Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.289 | 38966 |
| 2026-09-04T12:00:02.1164014Z | 2026-09-04T12:00:13.1283607Z | Vendoring sources to "/checkout" | 0.184 | 39150 |
| 2026-09-04T12:00:13.1284840Z | 2026-09-04T12:00:13.1287781Z | generate-copyright | 0.000 | 41309 |
| 2026-09-04T12:00:13.1288199Z | 2026-09-04T12:00:18.5507002Z | Building stage1 generate-copyright (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.090 | 41313 |
| 2026-09-04T12:00:18.5507308Z | 2026-09-04T12:00:19.8791679Z | generate-copyright (continued) | 0.022 | 41458 |
| 2026-09-04T12:01:18.3153477Z | 2026-09-04T12:01:18.3975206Z | Vendoring sources to "/checkout/obj/build/tmp/tarball/rust-src/image/lib/rustlib/src/rust" | 0.001 | 45848 |
| 2026-09-04T12:01:24.5242006Z | 2026-09-04T12:01:25.5359552Z | Building stage2 cargo (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.017 | 45890 |
| 2026-09-04T12:01:33.2182932Z | 2026-09-04T12:03:37.8433473Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-unknown-linux-gnu) | 2.077 | 46289 |
| 2026-09-04T12:03:45.1130824Z | 2026-09-04T12:04:10.9980311Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.431 | 46782 |
| 2026-09-04T12:04:10.9986558Z | 2026-09-04T12:04:11.1027867Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 46957 |
| 2026-09-04T12:04:12.6805118Z | 2026-09-04T12:04:12.9705997Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.005 | 47068 |
| 2026-09-04T12:04:12.9712157Z | 2026-09-04T12:04:13.0763999Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 47171 |
| 2026-09-04T12:04:16.6850220Z | 2026-09-04T12:05:02.0465329Z | Building stage2 miri (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.756 | 47278 |
| 2026-09-04T12:05:02.0471427Z | 2026-09-04T12:05:08.0677647Z | Building stage2 cargo-miri (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.100 | 47517 |
| 2026-09-04T12:05:41.0974192Z | 2026-09-04T12:05:54.0050744Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage2 -> stage2, aarch64-unknown-linux-gnu) | 0.215 | 47612 |
| 2026-09-04T12:07:18.2583816Z | 2026-09-04T12:07:36.4879757Z | Building stage2 build-manifest (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.304 | 47694 |
| 2026-09-04T12:07:56.3778674Z | 2026-09-04T12:08:06.0783546Z | Building bootstrap | 0.162 | 48149 |
| 2026-09-04T12:08:06.6336537Z | 2026-09-04T12:08:14.9851269Z | Building stage1 compiletest (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.139 | 48216 |
| 2026-09-04T12:08:14.9899145Z | 2026-09-04T12:08:17.4145708Z | Testing stage0 with compiletest suite=assembly-llvm mode=assembly (aarch64-unknown-linux-gnu) | 0.040 | 48295 |
| 2026-09-04T12:08:17.4159548Z | 2026-09-04T12:08:19.7688184Z | Testing stage0 with compiletest suite=codegen-llvm mode=codegen (aarch64-unknown-linux-gnu) | 0.039 | 49075 |
| 2026-09-04T12:08:19.7702183Z | 2026-09-04T12:08:19.9347958Z | Testing stage0 with compiletest suite=codegen-units mode=codegen-units (aarch64-unknown-linux-gnu) | 0.003 | 50302 |
| 2026-09-04T12:08:19.9361782Z | 2026-09-04T12:08:19.9875011Z | Building test helpers for aarch64-unknown-linux-gnu | 0.001 | 50355 |
| 2026-09-04T12:08:19.9882877Z | 2026-09-04T12:08:24.0839604Z | Testing stage0 with compiletest suite=incremental mode=incremental (aarch64-unknown-linux-gnu) | 0.068 | 50357 |
| 2026-09-04T12:08:24.0853715Z | 2026-09-04T12:08:25.2623607Z | Testing stage0 with compiletest suite=mir-opt mode=mir-opt (aarch64-unknown-linux-gnu) | 0.020 | 50544 |
| 2026-09-04T12:08:25.2637637Z | 2026-09-04T12:08:25.6328679Z | Testing stage0 with compiletest suite=pretty mode=pretty (aarch64-unknown-linux-gnu) | 0.006 | 50961 |
| 2026-09-04T12:08:25.6343557Z | 2026-09-04T12:08:30.6699978Z | Building stage1 run_make_support (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.084 | 51082 |
| 2026-09-04T12:08:30.6702221Z | 2026-09-04T12:08:30.7147471Z | Testing stage0 with compiletest suite=run-make mode=run-make (aarch64-unknown-linux-gnu) | 0.001 | 51112 |
| 2026-09-04T12:08:30.7163321Z | 2026-09-04T12:09:31.4914453Z | Testing stage0 with compiletest suite=ui mode=ui (aarch64-unknown-linux-gnu) | 1.013 | 51121 |
| 2026-09-04T12:09:31.4932340Z | 2026-09-04T12:09:31.8269893Z | Testing stage0 with compiletest suite=crashes mode=crashes (aarch64-unknown-linux-gnu) | 0.006 | 73311 |
| 2026-09-04T12:09:31.8287880Z | 2026-09-04T12:09:39.8484833Z | Testing stage0 with compiletest suite=rustdoc-html mode=rustdoc-html (aarch64-unknown-linux-gnu) | 0.134 | 73520 |
| 2026-09-04T12:09:39.8586706Z | 2026-09-04T12:09:39.8608645Z | sccache stats | 0.000 | 74377 |
| 2026-09-04T12:09:39.8608887Z | 2026-09-04T12:09:39.9130005Z | Clock drift check | 0.001 | 74420 |
| 2026-09-04T11:58:40.9375715Z | 2026-09-04T11:58:59.9389254Z | Dist rust-docs-nightly-aarch64-unknown-linux-gnu | 0.317 | 38797 |
| 2026-09-04T11:59:00.4912614Z | 2026-09-04T11:59:33.8443456Z | Dist rustc-docs-nightly-aarch64-unknown-linux-gnu | 0.556 | 38801 |
| 2026-09-04T11:59:40.3132435Z | 2026-09-04T11:59:44.4028832Z | Dist rust-docs-json-nightly-aarch64-unknown-linux-gnu | 0.068 | 38848 |
| 2026-09-04T12:00:19.8911869Z | 2026-09-04T12:00:36.9027678Z | Dist rustc-nightly-aarch64-unknown-linux-gnu | 0.284 | 45827 |
| 2026-09-04T12:00:36.9104904Z | 2026-09-04T12:00:39.3089942Z | Dist rustc-codegen-cranelift-nightly-aarch64-unknown-linux-gnu | 0.040 | 45831 |
| 2026-09-04T12:00:39.3154341Z | 2026-09-04T12:00:46.9792626Z | Dist rust-std-nightly-aarch64-unknown-linux-gnu | 0.128 | 45835 |
| 2026-09-04T12:00:47.1275773Z | 2026-09-04T12:01:17.5846011Z | Dist rustc-dev-nightly-aarch64-unknown-linux-gnu | 0.508 | 45839 |
| 2026-09-04T12:01:17.5902589Z | 2026-09-04T12:01:17.6110224Z | Dist rust-analysis-nightly-aarch64-unknown-linux-gnu | 0.000 | 45843 |
| 2026-09-04T12:01:18.4028917Z | 2026-09-04T12:01:24.5237374Z | Dist rust-src-nightly | 0.102 | 45884 |
| 2026-09-04T12:01:25.5471264Z | 2026-09-04T12:01:33.2175942Z | Dist cargo-nightly-aarch64-unknown-linux-gnu | 0.128 | 46283 |
| 2026-09-04T12:03:37.8508691Z | 2026-09-04T12:03:45.1124360Z | Dist rust-analyzer-nightly-aarch64-unknown-linux-gnu | 0.121 | 46776 |
| 2026-09-04T12:04:11.1103314Z | 2026-09-04T12:04:12.6798711Z | Dist rustfmt-nightly-aarch64-unknown-linux-gnu | 0.026 | 47062 |
| 2026-09-04T12:04:13.0841223Z | 2026-09-04T12:04:16.6843644Z | Dist clippy-nightly-aarch64-unknown-linux-gnu | 0.060 | 47272 |
| 2026-09-04T12:05:08.0758058Z | 2026-09-04T12:05:10.1262443Z | Dist miri-nightly-aarch64-unknown-linux-gnu | 0.034 | 47591 |
| 2026-09-04T12:05:10.1332585Z | 2026-09-04T12:05:19.6504195Z | Dist llvm-tools-nightly-aarch64-unknown-linux-gnu | 0.159 | 47595 |
| 2026-09-04T12:05:19.6565659Z | 2026-09-04T12:05:20.0928670Z | Dist llvm-bitcode-linker-nightly-aarch64-unknown-linux-gnu | 0.007 | 47599 |
| 2026-09-04T12:05:21.1726110Z | 2026-09-04T12:05:41.0967461Z | Dist rust-dev-nightly-aarch64-unknown-linux-gnu | 0.332 | 47605 |
| 2026-09-04T12:05:54.0152973Z | 2026-09-04T12:05:58.0894637Z | Dist rust-docs-json-nightly-aarch64-unknown-linux-gnu | 0.068 | 47681 |
| 2026-09-04T12:05:58.0957647Z | 2026-09-04T12:07:05.5290493Z | Dist rust-nightly-aarch64-unknown-linux-gnu | 1.124 | 47684 |
| 2026-09-04T12:07:06.1082189Z | 2026-09-04T12:07:18.2579342Z | Dist reproducible-artifacts-nightly-aarch64-unknown-linux-gnu | 0.202 | 47688 |
| 2026-09-04T12:07:36.4937114Z | 2026-09-04T12:07:36.9056305Z | Dist build-manifest-nightly-aarch64-unknown-linux-gnu | 0.007 | 47816 |
| 2026-09-04T12:07:36.9112769Z | 2026-09-04T12:07:42.6707490Z | Dist bootstrap-nightly-aarch64-unknown-linux-gnu | 0.096 | 47820 |
| 2026-09-04T12:07:49.4943664Z | 2026-09-04T12:07:51.3340583Z | Dist enzyme-nightly-aarch64-unknown-linux-gnu | 0.031 | 47963 |

</details>

| opt-dist timer (nested) | Minutes |
|---|---:|
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Build PGO instrumented rustc and LLVM | 20.598 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather rustc profiles | 4.707 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather rustdoc profiles | 0.512 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather clippy profiles | 0.836 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Build PGO optimized rustc | 9.426 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) | 36.080 |
| Stage 2 (LLVM PGO) > Build PGO instrumented LLVM | 3.619 |
| Stage 2 (LLVM PGO) > Gather profiles | 2.558 |
| Stage 2 (LLVM PGO) | 6.202 |
| Stage 5 (final build) | 24.107 |
| Run tests | 1.808 |

## [auto - dist-x86_64-linux: 100999915216](https://github.com/rust-lang/rust/actions/runs/33865610474/job/100999915216)

Run 33865610474; raw SHA256 `e4d8d5ba5d9d1cba89370c6ac1b1b04264d5ad87cfa9ed66b5261f773fd31db3`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 10.482 |
| Build support | 9.333 |
| LLVM/LLD | 15.357 |
| Compiler | 10.450 |
| Tools | 26.240 |
| Libraries | 0.492 |
| Tests | 17.073 |
| Docs | 4.183 |
| Packaging | 10.040 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-04T10:59:43.1419946Z | 2026-09-04T10:59:43.1436223Z | Run set +e | 0.000 | 1446 |
| 2026-09-04T10:59:43.1855071Z | 2026-09-04T10:59:43.1950280Z | Image checksum input | 0.000 | 1488 |
| 2026-09-04T10:59:43.1951127Z | 2026-09-04T11:00:01.7068060Z | Building docker image for dist-x86_64-linux | 0.309 | 1963 |
| 2026-09-04T11:00:04.5178271Z | 2026-09-04T11:00:04.5278552Z | Clock drift check | 0.000 | 2046 |
| 2026-09-04T11:00:04.8597260Z | 2026-09-04T11:00:04.8609436Z | Configure the build | 0.000 | 2052 |
| 2026-09-04T11:00:14.5545674Z | 2026-09-04T11:00:24.5201786Z | Building bootstrap | 0.166 | 2104 |
| 2026-09-04T11:00:24.6730768Z | 2026-09-04T11:00:24.6731094Z | Building LLVM for x86_64-unknown-linux-gnu | 0.000 | 2235 |
| 2026-09-04T11:00:24.6732726Z | 2026-09-04T11:00:24.6734370Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2237 |
| 2026-09-04T11:00:24.6735071Z | 2026-09-04T11:00:24.6735390Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2240 |
| 2026-09-04T11:00:24.6735712Z | 2026-09-04T11:00:24.6736009Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2242 |
| 2026-09-04T11:00:24.6736975Z | 2026-09-04T11:00:24.6737288Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2244 |
| 2026-09-04T11:00:24.6737771Z | 2026-09-04T11:00:24.6738088Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2246 |
| 2026-09-04T11:00:24.6740745Z | 2026-09-04T11:00:24.6741050Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2248 |
| 2026-09-04T11:00:24.6742119Z | 2026-09-04T11:00:24.6742427Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2250 |
| 2026-09-04T11:00:24.6743145Z | 2026-09-04T11:00:24.6743466Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2253 |
| 2026-09-04T11:00:24.6744215Z | 2026-09-04T11:00:24.6744504Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2255 |
| 2026-09-04T11:00:24.6745552Z | 2026-09-04T11:00:24.6745854Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2257 |
| 2026-09-04T11:00:24.6746536Z | 2026-09-04T11:00:24.6746840Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2259 |
| 2026-09-04T11:00:24.6749494Z | 2026-09-04T11:00:24.6749907Z | Building stage2 cargo (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2262 |
| 2026-09-04T11:00:24.6751145Z | 2026-09-04T11:00:24.6751448Z | Building stage2 rust-analyzer (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2264 |
| 2026-09-04T11:00:24.6752391Z | 2026-09-04T11:00:24.6752729Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2266 |
| 2026-09-04T11:00:24.6753874Z | 2026-09-04T11:00:24.6754191Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2268 |
| 2026-09-04T11:00:24.6755036Z | 2026-09-04T11:00:24.6755337Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2270 |
| 2026-09-04T11:00:24.6756086Z | 2026-09-04T11:00:24.6756389Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2272 |
| 2026-09-04T11:00:24.6757160Z | 2026-09-04T11:00:24.6757698Z | Building stage2 rustfmt (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2274 |
| 2026-09-04T11:00:24.6758145Z | 2026-09-04T11:00:24.6758451Z | Building stage2 cargo-fmt (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2276 |
| 2026-09-04T11:00:24.6759143Z | 2026-09-04T11:00:24.6759523Z | Building stage2 miri (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2278 |
| 2026-09-04T11:00:24.6760717Z | 2026-09-04T11:00:24.6761010Z | Building stage2 cargo-miri (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2280 |
| 2026-09-04T11:00:24.6853485Z | 2026-09-04T11:00:24.6976157Z | Display CPU and Memory information | 0.000 | 2283 |
| 2026-09-04T11:00:24.7388933Z | 2026-09-04T11:00:24.7728391Z | Building bootstrap | 0.001 | 2794 |
| 2026-09-04T11:00:24.9281394Z | 2026-09-04T11:00:38.1644738Z | Building stage1 opt-dist (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.221 | 2807 |
| 2026-09-04T11:00:38.1761870Z | 2026-09-04T11:00:38.1774927Z | Environment values | 0.000 | 3031 |
| 2026-09-04T11:00:38.1775144Z | 2026-09-04T11:00:38.1814481Z | Printing bootstrap.toml | 0.000 | 3085 |
| 2026-09-04T11:00:38.1815587Z | 2026-09-04T11:00:59.7241713Z | Building rustc-perf | 0.359 | 3296 |
| 2026-09-04T11:00:59.7738648Z | 2026-09-04T11:00:59.8077978Z | Building bootstrap | 0.001 | 3835 |
| 2026-09-04T11:00:59.9724926Z | 2026-09-04T11:02:17.0191191Z | Building LLVM for x86_64-unknown-linux-gnu | 1.284 | 3846 |
| 2026-09-04T11:02:17.0312324Z | 2026-09-04T11:06:41.5421127Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-unknown-linux-gnu) | 4.409 | 11424 |
| 2026-09-04T11:06:41.7398805Z | 2026-09-04T11:08:05.1383893Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-unknown-linux-gnu) | 1.390 | 12116 |
| 2026-09-04T11:08:05.1387360Z | 2026-09-04T11:08:08.1356766Z | Building LLD for x86_64-unknown-linux-gnu | 0.050 | 12235 |
| 2026-09-04T11:08:08.1361119Z | 2026-09-04T11:08:08.3712212Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.004 | 12507 |
| 2026-09-04T11:08:08.3716936Z | 2026-09-04T11:08:24.7427966Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.273 | 12516 |
| 2026-09-04T11:08:24.7432644Z | 2026-09-04T11:08:28.1877269Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.057 | 12655 |
| 2026-09-04T11:08:28.2935252Z | 2026-09-04T11:08:36.8015113Z | Building sanitizers for x86_64-unknown-linux-gnu | 0.142 | 12728 |
| 2026-09-04T11:08:36.8021818Z | 2026-09-04T11:09:06.0789529Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-unknown-linux-gnu) | 0.488 | 13499 |
| 2026-09-04T11:09:06.0849255Z | 2026-09-04T11:11:56.6024804Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-unknown-linux-gnu) | 2.842 | 13575 |
| 2026-09-04T11:11:56.6042822Z | 2026-09-04T11:13:47.1056089Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-unknown-linux-gnu) | 1.842 | 14164 |
| 2026-09-04T11:13:47.1061161Z | 2026-09-04T11:13:47.4049988Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.005 | 14258 |
| 2026-09-04T11:13:47.4055380Z | 2026-09-04T11:14:10.0631777Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.378 | 14267 |
| 2026-09-04T11:14:10.0636810Z | 2026-09-04T11:14:14.4909544Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.074 | 14394 |
| 2026-09-04T11:14:14.4926180Z | 2026-09-04T11:15:53.8426029Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, x86_64-unknown-linux-gnu) | 1.656 | 14468 |
| 2026-09-04T11:15:53.9361108Z | 2026-09-04T11:20:03.9286250Z | Building stage2 cargo (stage1 -> stage2, x86_64-unknown-linux-gnu) | 4.167 | 14665 |
| 2026-09-04T11:20:03.9293197Z | 2026-09-04T11:22:05.4451819Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-unknown-linux-gnu) | 2.025 | 15554 |
| 2026-09-04T11:22:05.4457598Z | 2026-09-04T11:22:05.5533553Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.002 | 15738 |
| 2026-09-04T11:22:05.5645880Z | 2026-09-04T11:25:45.2948172Z | Running benchmarks | 3.662 | 15893 |
| 2026-09-04T11:26:53.2121568Z | 2026-09-04T11:27:17.5095393Z | Running benchmarks | 0.405 | 15962 |
| 2026-09-04T11:27:25.8889880Z | 2026-09-04T11:28:06.7007377Z | Running benchmarks | 0.680 | 16016 |
| 2026-09-04T11:28:16.4475361Z | 2026-09-04T11:28:16.7898892Z | Building bootstrap | 0.006 | 16075 |
| 2026-09-04T11:28:17.6846611Z | 2026-09-04T11:28:19.6211239Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.032 | 16101 |
| 2026-09-04T11:28:19.8206050Z | 2026-09-04T11:28:20.1628089Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.006 | 16424 |
| 2026-09-04T11:28:20.1638184Z | 2026-09-04T11:28:20.2340793Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.001 | 16481 |
| 2026-09-04T11:28:20.2351253Z | 2026-09-04T11:28:20.6294727Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.007 | 16489 |
| 2026-09-04T11:28:20.6299121Z | 2026-09-04T11:28:20.7803119Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.003 | 16561 |
| 2026-09-04T11:28:20.9974807Z | 2026-09-04T11:28:21.2219344Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-unknown-linux-gnu) | 0.004 | 16613 |
| 2026-09-04T11:28:21.2278195Z | 2026-09-04T11:31:31.2630559Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-unknown-linux-gnu) | 3.167 | 16655 |
| 2026-09-04T11:31:31.4588205Z | 2026-09-04T11:31:46.2071335Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.246 | 17212 |
| 2026-09-04T11:31:46.2076242Z | 2026-09-04T11:31:46.2801807Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.001 | 17268 |
| 2026-09-04T11:31:46.2806001Z | 2026-09-04T11:31:46.6585384Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.006 | 17276 |
| 2026-09-04T11:31:46.6590107Z | 2026-09-04T11:31:46.8110635Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.003 | 17348 |
| 2026-09-04T11:31:46.8125793Z | 2026-09-04T11:33:11.7859147Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, x86_64-unknown-linux-gnu) | 1.416 | 17403 |
| 2026-09-04T11:33:11.8777588Z | 2026-09-04T11:36:29.2990945Z | Building stage2 cargo (stage1 -> stage2, x86_64-unknown-linux-gnu) | 3.290 | 17569 |
| 2026-09-04T11:36:29.2997400Z | 2026-09-04T11:38:14.5363949Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-unknown-linux-gnu) | 1.754 | 18277 |
| 2026-09-04T11:38:14.5369422Z | 2026-09-04T11:38:14.6551320Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.002 | 18447 |
| 2026-09-04T11:38:15.9263089Z | 2026-09-04T11:38:15.9806067Z | Building bootstrap | 0.001 | 18606 |
| 2026-09-04T11:38:16.1553253Z | 2026-09-04T11:41:41.6981122Z | Building LLVM for x86_64-unknown-linux-gnu | 3.426 | 18617 |
| 2026-09-04T11:41:41.7078546Z | 2026-09-04T11:41:48.6793982Z | Building LLD for x86_64-unknown-linux-gnu | 0.116 | 26210 |
| 2026-09-04T11:41:48.6798305Z | 2026-09-04T11:41:48.7453987Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.001 | 26486 |
| 2026-09-04T11:41:48.7458469Z | 2026-09-04T11:41:48.8367299Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.002 | 26494 |
| 2026-09-04T11:41:48.8371261Z | 2026-09-04T11:41:48.9190980Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.001 | 26566 |
| 2026-09-04T11:41:49.0276314Z | 2026-09-04T11:41:49.0925005Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.001 | 26633 |
| 2026-09-04T11:41:49.0928944Z | 2026-09-04T11:41:49.1696479Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.001 | 26641 |
| 2026-09-04T11:41:49.1701412Z | 2026-09-04T11:41:49.2430751Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.001 | 26713 |
| 2026-09-04T11:41:49.2545081Z | 2026-09-04T11:44:44.9266723Z | Running benchmarks | 2.928 | 26767 |
| 2026-09-04T11:45:18.0958079Z | 2026-09-04T11:45:18.4149121Z | Building bootstrap | 0.005 | 26871 |
| 2026-09-04T11:45:18.6893838Z | 2026-09-04T11:55:40.4419974Z | Building LLVM for x86_64-unknown-linux-gnu | 10.363 | 26882 |
| 2026-09-04T11:55:40.8894403Z | 2026-09-04T11:55:47.9821407Z | Building LLD for x86_64-unknown-linux-gnu | 0.118 | 34475 |
| 2026-09-04T11:55:47.9825833Z | 2026-09-04T11:55:48.1426824Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.003 | 34751 |
| 2026-09-04T11:55:48.1430997Z | 2026-09-04T11:55:48.4921472Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.006 | 34759 |
| 2026-09-04T11:55:48.4925989Z | 2026-09-04T11:55:48.6217529Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.002 | 34831 |
| 2026-09-04T11:55:48.9687175Z | 2026-09-04T11:55:49.0372237Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.001 | 34898 |
| 2026-09-04T11:55:49.0376213Z | 2026-09-04T11:55:49.3301969Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.005 | 34906 |
| 2026-09-04T11:55:49.3306395Z | 2026-09-04T11:55:49.4491427Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.002 | 34978 |
| 2026-09-04T11:56:37.2457260Z | 2026-09-04T11:59:22.3488429Z | Running benchmarks | 2.752 | 35120 |
| 2026-09-04T11:59:22.3496213Z | 2026-09-04T12:00:34.3294494Z | Merging BOLT profiles | 1.200 | 35164 |
| 2026-09-04T12:01:20.4091149Z | 2026-09-04T12:06:35.9914318Z | Running benchmarks | 5.260 | 35223 |
| 2026-09-04T12:06:35.9924777Z | 2026-09-04T12:09:34.6188072Z | Merging BOLT profiles | 2.977 | 35286 |
| 2026-09-04T12:11:28.4166404Z | 2026-09-04T12:11:28.6420212Z | Building bootstrap | 0.004 | 35443 |
| 2026-09-04T12:11:29.4163814Z | 2026-09-04T12:11:29.5495852Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.002 | 35478 |
| 2026-09-04T12:11:29.5499879Z | 2026-09-04T12:11:29.7907333Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.004 | 35486 |
| 2026-09-04T12:11:29.7912005Z | 2026-09-04T12:11:29.9123647Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.002 | 35558 |
| 2026-09-04T12:11:30.0335252Z | 2026-09-04T12:11:42.0140764Z | Building stage1 unstable-book-gen (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.200 | 35618 |
| 2026-09-04T12:11:44.4468586Z | 2026-09-04T12:12:02.3645119Z | Building stage1 rustbook (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.299 | 35850 |
| 2026-09-04T12:12:05.4176238Z | 2026-09-04T12:12:05.4200735Z | Documenting stage2 book redirect pages (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 36277 |
| 2026-09-04T12:12:05.4201074Z | 2026-09-04T12:13:10.1814660Z | Building stage1 rustdoc-tool-binary (stage0 -> stage1, x86_64-unknown-linux-gnu) | 1.079 | 36281 |
| 2026-09-04T12:13:10.1815016Z | 2026-09-04T12:13:10.7572394Z | Documenting stage2 book redirect pages (stage1 -> stage2, x86_64-unknown-linux-gnu) (continued) | 0.010 | 36464 |
| 2026-09-04T12:13:10.7574052Z | 2026-09-04T12:13:10.9448028Z | Documenting stage2 standalone (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.003 | 36470 |
| 2026-09-04T12:13:10.9452934Z | 2026-09-04T12:13:27.7858438Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage1 -> stage1, x86_64-unknown-linux-gnu) | 0.281 | 36474 |
| 2026-09-04T12:13:27.7876055Z | 2026-09-04T12:14:14.2635067Z | Documenting stage2 compiler{rustc-main, rustc_abi, rustc_arena, rustc_ast, rustc_ast_ir, rustc_ast_lowering, rustc_ast_passes, rustc_ast_pretty, rustc_attr_ir, rustc_attr_parsing, rustc_baked_icu_data, rustc_borrowck, rustc_builtin_macros, rustc_codegen_llvm, rustc_codegen_ssa, rustc_const_eval, rustc_crate_store, rustc_data_structures, rustc_driver, rustc_driver_impl, rustc_error_codes, rustc_error_messages, rustc_errors, rustc_expand, rustc_feature, rustc_fs_util, rustc_graphviz, rustc_hashes, rustc_hir, rustc_hir_analysis, rustc_hir_id, rustc_hir_pretty, rustc_hir_typeck, rustc_incremental, rustc_index, rustc_index_macros, rustc_infer, rustc_interface, rustc_lexer, rustc_lint, rustc_lint_defs, rustc_llvm, rustc_log, rustc_macros, rustc_metadata, rustc_middle, rustc_mir_build, rustc_mir_dataflow, rustc_mir_transform, rustc_monomorphize, rustc_next_trait_solver, rustc_parse, rustc_parse_format, rustc_passes, rustc_pattern_analysis, rustc_privacy, rustc_proc_macro, rustc_public, rustc_public_bridge, rustc_query_impl, rustc_resolve, rustc_sanitizers, rustc_serialize, rustc_session, rustc_span, rustc_structures, rustc_symbol_mangling, rustc_target, rustc_thread_pool, rustc_trait_selection, rustc_traits, rustc_transmute, rustc_ty_utils, rustc_ty_walk, rustc_type_ir, rustc_type_ir_macros, rustc_windows_rc} (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.775 | 36543 |
| 2026-09-04T12:14:14.4660769Z | 2026-09-04T12:14:14.5352704Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.001 | 37219 |
| 2026-09-04T12:14:14.5356562Z | 2026-09-04T12:14:14.7498904Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.004 | 37227 |
| 2026-09-04T12:14:14.7503499Z | 2026-09-04T12:14:14.8615126Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.002 | 37299 |
| 2026-09-04T12:14:14.8626156Z | 2026-09-04T12:14:25.7434383Z | Documenting stage2 rustdoc (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.181 | 37346 |
| 2026-09-04T12:14:25.7443030Z | 2026-09-04T12:14:33.6957803Z | Documenting stage2 rustfmt (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.133 | 37533 |
| 2026-09-04T12:14:33.6963209Z | 2026-09-04T12:14:46.3233887Z | Building stage2 error_index_generator (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.210 | 37718 |
| 2026-09-04T12:15:07.7088173Z | 2026-09-04T12:15:10.2379478Z | Building stage1 lint-docs (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.042 | 38055 |
| 2026-09-04T12:15:10.2419956Z | 2026-09-04T12:15:19.9771585Z | Running stage2 lint-docs (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.162 | 38089 |
| 2026-09-04T12:15:20.3446807Z | 2026-09-04T12:16:05.3734722Z | Documenting stage2 cargo (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.750 | 38102 |
| 2026-09-04T12:16:05.7239701Z | 2026-09-04T12:16:08.7312557Z | Documenting stage2 clippy (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.050 | 38930 |
| 2026-09-04T12:16:08.8348743Z | 2026-09-04T12:16:08.8364921Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 38973 |
| 2026-09-04T12:16:08.8365206Z | 2026-09-04T12:16:25.6026929Z | Documenting stage2 miri (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.279 | 38976 |
| 2026-09-04T12:16:25.6027288Z | 2026-09-04T12:16:25.6030838Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, x86_64-unknown-linux-gnu) (continued) | 0.000 | 39144 |
| 2026-09-04T12:16:25.6031104Z | 2026-09-04T12:16:32.0621815Z | Documenting stage2 tidy (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.108 | 39148 |
| 2026-09-04T12:16:32.0622183Z | 2026-09-04T12:16:32.0625024Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, x86_64-unknown-linux-gnu) (continued) | 0.000 | 39365 |
| 2026-09-04T12:16:32.0625304Z | 2026-09-04T12:16:41.8798223Z | Documenting stage2 bootstrap (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.164 | 39369 |
| 2026-09-04T12:16:41.8798567Z | 2026-09-04T12:16:41.8802095Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, x86_64-unknown-linux-gnu) (continued) | 0.000 | 39534 |
| 2026-09-04T12:16:41.8802382Z | 2026-09-04T12:16:42.7257942Z | Documenting stage2 buildhelper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.014 | 39538 |
| 2026-09-04T12:16:42.7258316Z | 2026-09-04T12:16:42.7261186Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, x86_64-unknown-linux-gnu) (continued) | 0.000 | 39545 |
| 2026-09-04T12:16:42.7261473Z | 2026-09-04T12:16:47.4794763Z | Documenting stage2 compiletest (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.079 | 39549 |
| 2026-09-04T12:16:47.4795163Z | 2026-09-04T12:16:47.4798043Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, x86_64-unknown-linux-gnu) (continued) | 0.000 | 39691 |
| 2026-09-04T12:16:47.4798365Z | 2026-09-04T12:16:52.3245379Z | Documenting stage2 runmakesupport (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.081 | 39695 |
| 2026-09-04T12:16:52.3245759Z | 2026-09-04T12:16:55.4967810Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, x86_64-unknown-linux-gnu) (continued) | 0.053 | 39778 |
| 2026-09-04T12:16:55.7639221Z | 2026-09-04T12:16:55.8064802Z | Documenting stage2 releases (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.001 | 39811 |
| 2026-09-04T12:16:56.3213356Z | 2026-09-04T12:17:07.1179210Z | Building stage1 rust-installer (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.180 | 39816 |
| 2026-09-04T12:17:56.9177487Z | 2026-09-04T12:18:04.0850456Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage1 -> stage1, x86_64-unknown-linux-gnu) | 0.119 | 39904 |
| 2026-09-04T12:18:08.1786359Z | 2026-09-04T12:18:37.6470592Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.491 | 39954 |
| 2026-09-04T12:18:37.7386863Z | 2026-09-04T12:18:55.9332532Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.303 | 40063 |
| 2026-09-04T12:18:55.9558479Z | 2026-09-04T12:19:04.9058366Z | Vendoring sources to "/checkout" | 0.149 | 40247 |
| 2026-09-04T12:19:04.9060416Z | 2026-09-04T12:19:04.9063151Z | generate-copyright | 0.000 | 42405 |
| 2026-09-04T12:19:04.9063437Z | 2026-09-04T12:19:09.6731071Z | Building stage1 generate-copyright (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.079 | 42409 |
| 2026-09-04T12:19:09.6731318Z | 2026-09-04T12:19:10.8949201Z | generate-copyright (continued) | 0.020 | 42554 |
| 2026-09-04T12:20:21.6063577Z | 2026-09-04T12:20:21.6736888Z | Vendoring sources to "/checkout/obj/build/tmp/tarball/rust-src/image/lib/rustlib/src/rust" | 0.001 | 46944 |
| 2026-09-04T12:20:27.1069604Z | 2026-09-04T12:20:28.0622810Z | Building stage2 cargo (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.016 | 46986 |
| 2026-09-04T12:20:35.6888453Z | 2026-09-04T12:22:46.8257153Z | Building stage2 rust-analyzer (stage1 -> stage2, x86_64-unknown-linux-gnu) | 2.186 | 47385 |
| 2026-09-04T12:22:53.8427662Z | 2026-09-04T12:23:20.6024169Z | Building stage2 rustfmt (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.446 | 47878 |
| 2026-09-04T12:23:20.6029706Z | 2026-09-04T12:23:20.7084809Z | Building stage2 cargo-fmt (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.002 | 48053 |
| 2026-09-04T12:23:22.2937007Z | 2026-09-04T12:23:58.2181512Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.599 | 48164 |
| 2026-09-04T12:23:58.2186861Z | 2026-09-04T12:23:58.3238316Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.002 | 48268 |
| 2026-09-04T12:24:01.9733284Z | 2026-09-04T12:24:51.4988664Z | Building stage2 miri (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.825 | 48375 |
| 2026-09-04T12:24:51.4994780Z | 2026-09-04T12:24:57.6224161Z | Building stage2 cargo-miri (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.102 | 48617 |
| 2026-09-04T12:25:46.4232717Z | 2026-09-04T12:25:57.8090043Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage2 -> stage2, x86_64-unknown-linux-gnu) | 0.190 | 48712 |
| 2026-09-04T12:29:01.7631265Z | 2026-09-04T12:29:10.5417187Z | Vendoring sources to "/checkout/obj/build/tmp/tarball/rustc/src/image" | 0.146 | 48789 |
| 2026-09-04T12:33:10.8122142Z | 2026-09-04T12:33:22.7761720Z | Vendoring sources to "/checkout/obj/build/tmp/tarball/rustc/src-gpl/image" | 0.199 | 50906 |
| 2026-09-04T12:36:23.6745163Z | 2026-09-04T12:36:41.7175920Z | Building stage2 build-manifest (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.301 | 52854 |
| 2026-09-04T12:37:07.4203653Z | 2026-09-04T12:37:30.8808660Z | Building stage2 codegen backend gcc (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.391 | 53743 |
| 2026-09-04T12:37:38.3867759Z | 2026-09-04T12:37:48.0789580Z | Building bootstrap | 0.162 | 53975 |
| 2026-09-04T12:37:48.5803393Z | 2026-09-04T12:37:56.7288450Z | Building stage1 compiletest (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.136 | 54042 |
| 2026-09-04T12:37:56.7339763Z | 2026-09-04T12:37:58.9907540Z | Testing stage0 with compiletest suite=assembly-llvm mode=assembly (x86_64-unknown-linux-gnu) | 0.038 | 54121 |
| 2026-09-04T12:37:58.9921715Z | 2026-09-04T12:38:01.1107667Z | Testing stage0 with compiletest suite=codegen-llvm mode=codegen (x86_64-unknown-linux-gnu) | 0.035 | 54901 |
| 2026-09-04T12:38:01.1121772Z | 2026-09-04T12:38:01.2683684Z | Testing stage0 with compiletest suite=codegen-units mode=codegen-units (x86_64-unknown-linux-gnu) | 0.003 | 56128 |
| 2026-09-04T12:38:01.2696782Z | 2026-09-04T12:38:01.3227950Z | Building test helpers for x86_64-unknown-linux-gnu | 0.001 | 56181 |
| 2026-09-04T12:38:01.3229525Z | 2026-09-04T12:38:05.3745680Z | Testing stage0 with compiletest suite=incremental mode=incremental (x86_64-unknown-linux-gnu) | 0.068 | 56183 |
| 2026-09-04T12:38:05.3759624Z | 2026-09-04T12:38:06.5005346Z | Testing stage0 with compiletest suite=mir-opt mode=mir-opt (x86_64-unknown-linux-gnu) | 0.019 | 56370 |
| 2026-09-04T12:38:06.5019244Z | 2026-09-04T12:38:06.7548049Z | Testing stage0 with compiletest suite=pretty mode=pretty (x86_64-unknown-linux-gnu) | 0.004 | 56787 |
| 2026-09-04T12:38:06.7562040Z | 2026-09-04T12:38:12.0738417Z | Building stage1 run_make_support (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.089 | 56908 |
| 2026-09-04T12:38:12.0741712Z | 2026-09-04T12:38:12.3170542Z | Testing stage0 with compiletest suite=run-make mode=run-make (x86_64-unknown-linux-gnu) | 0.004 | 56938 |
| 2026-09-04T12:38:12.3187199Z | 2026-09-04T12:39:16.9834330Z | Testing stage0 with compiletest suite=ui mode=ui (x86_64-unknown-linux-gnu) | 1.078 | 56947 |
| 2026-09-04T12:39:16.9851655Z | 2026-09-04T12:39:17.2614535Z | Testing stage0 with compiletest suite=crashes mode=crashes (x86_64-unknown-linux-gnu) | 0.005 | 79137 |
| 2026-09-04T12:39:17.2632159Z | 2026-09-04T12:39:25.2871688Z | Testing stage0 with compiletest suite=rustdoc-html mode=rustdoc-html (x86_64-unknown-linux-gnu) | 0.134 | 79346 |
| 2026-09-04T12:39:25.3514043Z | 2026-09-04T12:39:34.7862974Z | Building bootstrap | 0.157 | 80216 |
| 2026-09-04T12:39:35.1919907Z | 2026-09-04T12:42:54.7844385Z | Building GCC for x86_64-unknown-linux-gnu -> x86_64-unknown-linux-gnu | 3.327 | 80224 |
| 2026-09-04T12:42:54.7876731Z | 2026-09-04T12:43:03.5562115Z | Building stage1 rust-installer (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.146 | 81072 |
| 2026-09-04T12:43:19.8243167Z | 2026-09-04T12:43:19.8273880Z | sccache stats | 0.000 | 81188 |
| 2026-09-04T12:43:19.8274099Z | 2026-09-04T12:43:19.8835683Z | Clock drift check | 0.001 | 81240 |
| 2026-09-04T12:17:07.1222343Z | 2026-09-04T12:17:25.0934497Z | Dist rust-docs-nightly-x86_64-unknown-linux-gnu | 0.300 | 39895 |
| 2026-09-04T12:17:25.6492695Z | 2026-09-04T12:17:56.9172799Z | Dist rustc-docs-nightly-x86_64-unknown-linux-gnu | 0.521 | 39899 |
| 2026-09-04T12:18:04.0898324Z | 2026-09-04T12:18:08.1778274Z | Dist rust-docs-json-nightly-x86_64-unknown-linux-gnu | 0.068 | 39946 |
| 2026-09-04T12:19:10.9071721Z | 2026-09-04T12:19:34.9080055Z | Dist rustc-nightly-x86_64-unknown-linux-gnu | 0.400 | 46923 |
| 2026-09-04T12:19:34.9152372Z | 2026-09-04T12:19:37.2743739Z | Dist rustc-codegen-cranelift-nightly-x86_64-unknown-linux-gnu | 0.039 | 46927 |
| 2026-09-04T12:19:37.2805423Z | 2026-09-04T12:19:45.6168973Z | Dist rust-std-nightly-x86_64-unknown-linux-gnu | 0.139 | 46931 |
| 2026-09-04T12:19:45.7430083Z | 2026-09-04T12:20:20.8880863Z | Dist rustc-dev-nightly-x86_64-unknown-linux-gnu | 0.586 | 46935 |
| 2026-09-04T12:20:20.8928952Z | 2026-09-04T12:20:20.9103173Z | Dist rust-analysis-nightly-x86_64-unknown-linux-gnu | 0.000 | 46939 |
| 2026-09-04T12:20:21.6782976Z | 2026-09-04T12:20:27.1065475Z | Dist rust-src-nightly | 0.090 | 46980 |
| 2026-09-04T12:20:28.0720535Z | 2026-09-04T12:20:35.6883399Z | Dist cargo-nightly-x86_64-unknown-linux-gnu | 0.127 | 47379 |
| 2026-09-04T12:22:46.8323420Z | 2026-09-04T12:22:53.8422851Z | Dist rust-analyzer-nightly-x86_64-unknown-linux-gnu | 0.117 | 47872 |
| 2026-09-04T12:23:20.7151130Z | 2026-09-04T12:23:22.2930267Z | Dist rustfmt-nightly-x86_64-unknown-linux-gnu | 0.026 | 48158 |
| 2026-09-04T12:23:58.3308950Z | 2026-09-04T12:24:01.9727896Z | Dist clippy-nightly-x86_64-unknown-linux-gnu | 0.061 | 48369 |
| 2026-09-04T12:24:57.6294337Z | 2026-09-04T12:25:00.1677372Z | Dist miri-nightly-x86_64-unknown-linux-gnu | 0.042 | 48691 |
| 2026-09-04T12:25:00.1742458Z | 2026-09-04T12:25:13.3489308Z | Dist llvm-tools-nightly-x86_64-unknown-linux-gnu | 0.220 | 48695 |
| 2026-09-04T12:25:13.3545799Z | 2026-09-04T12:25:13.7422710Z | Dist llvm-bitcode-linker-nightly-x86_64-unknown-linux-gnu | 0.006 | 48699 |
| 2026-09-04T12:25:14.8153091Z | 2026-09-04T12:25:46.4224452Z | Dist rust-dev-nightly-x86_64-unknown-linux-gnu | 0.527 | 48705 |
| 2026-09-04T12:25:57.8186013Z | 2026-09-04T12:26:01.9769899Z | Dist rust-docs-json-nightly-x86_64-unknown-linux-gnu | 0.069 | 48781 |
| 2026-09-04T12:26:01.9817149Z | 2026-09-04T12:27:21.4520681Z | Dist rust-nightly-x86_64-unknown-linux-gnu | 1.325 | 48784 |
| 2026-09-04T12:29:11.3406531Z | 2026-09-04T12:31:10.0714685Z | Dist rustc-nightly-src | 1.979 | 50901 |
| 2026-09-04T12:33:24.7996837Z | 2026-09-04T12:35:59.1063728Z | Dist rustc-nightly-src-gpl | 2.572 | 52844 |
| 2026-09-04T12:36:00.6081868Z | 2026-09-04T12:36:23.6740214Z | Dist reproducible-artifacts-nightly-x86_64-unknown-linux-gnu | 0.384 | 52848 |
| 2026-09-04T12:36:41.7223122Z | 2026-09-04T12:36:42.0973015Z | Dist build-manifest-nightly-x86_64-unknown-linux-gnu | 0.006 | 52976 |
| 2026-09-04T12:36:42.1020530Z | 2026-09-04T12:36:47.7857201Z | Dist bootstrap-nightly-x86_64-unknown-linux-gnu | 0.095 | 52980 |
| 2026-09-04T12:36:53.0461671Z | 2026-09-04T12:36:54.9473296Z | Dist enzyme-nightly-x86_64-unknown-linux-gnu | 0.032 | 53123 |
| 2026-09-04T12:37:05.7776040Z | 2026-09-04T12:37:07.4197207Z | Dist offload-nightly-x86_64-unknown-linux-gnu | 0.027 | 53738 |
| 2026-09-04T12:37:30.8854772Z | 2026-09-04T12:37:31.5350443Z | Dist rustc-codegen-gcc-nightly-x86_64-unknown-linux-gnu | 0.011 | 53780 |
| 2026-09-04T12:43:03.5582359Z | 2026-09-04T12:43:11.7508666Z | Dist gcc-dev-nightly-x86_64-unknown-linux-gnu | 0.137 | 81173 |
| 2026-09-04T12:43:11.7533595Z | 2026-09-04T12:43:19.8036950Z | Dist gcc-x86_64-unknown-linux-gnu-nightly-x86_64-unknown-linux-gnu | 0.134 | 81177 |

</details>

| opt-dist timer (nested) | Minutes |
|---|---:|
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Build PGO instrumented rustc and LLVM | 21.097 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather rustc profiles | 4.794 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather rustdoc profiles | 0.545 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather clippy profiles | 0.839 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Build PGO optimized rustc | 9.974 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) | 37.249 |
| Stage 2 (LLVM PGO) > Build PGO instrumented LLVM | 3.556 |
| Stage 2 (LLVM PGO) > Gather profiles | 3.474 |
| Stage 2 (LLVM PGO) | 7.055 |
| Stage 3 (BOLT) > Build PGO optimized LLVM | 10.525 |
| Stage 3 (BOLT) > Instrument & gather profiles > Gather profiles | 3.968 |
| Stage 3 (BOLT) > Instrument & gather profiles | 4.782 |
| Stage 3 (BOLT) > Instrument & gather profiles > Gather profiles | 8.247 |
| Stage 3 (BOLT) > Instrument & gather profiles | 8.994 |
| Stage 3 (BOLT) > Optimize LLVM and rustc with BOLT | 1.871 |
| Stage 3 (BOLT) | 26.172 |
| Stage 5 (final build) | 26.054 |
| Run tests | 1.896 |

## [auto - i686-msvc-1: 100999917936](https://github.com/rust-lang/rust/actions/runs/33865610474/job/100999917936)

Run 33865610474; raw SHA256 `06aa24979e6b764549555006d4e07c35bfb9097b53513a1c8971176c8692d9b8`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 1.320 |
| Build support | 1.853 |
| LLVM/LLD | 14.752 |
| Compiler | 56.583 |
| Tools | 38.233 |
| Libraries | 1.749 |
| Tests | 63.519 |
| Docs | 4.291 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-04T11:03:40.0093531Z | 2026-09-04T11:03:40.0125536Z | Run set +e | 0.000 | 1791 |
| 2026-09-04T11:03:41.9192987Z | 2026-09-04T11:03:42.0896486Z | Clock drift check | 0.003 | 1837 |
| 2026-09-04T11:03:43.7964821Z | 2026-09-04T11:03:43.7998778Z | Configure the build | 0.000 | 1843 |
| 2026-09-04T11:03:55.0452360Z | 2026-09-04T11:05:45.5383273Z | Building bootstrap | 1.842 | 1889 |
| 2026-09-04T11:05:47.6453137Z | 2026-09-04T11:05:47.6526791Z | Building LLVM for i686-pc-windows-msvc | 0.000 | 2069 |
| 2026-09-04T11:05:47.6548896Z | 2026-09-04T11:05:47.6555946Z | Building stage1 compiler artifacts (stage0 -> stage1, i686-pc-windows-msvc) | 0.000 | 2071 |
| 2026-09-04T11:05:47.6561995Z | 2026-09-04T11:05:47.6563093Z | Building stage1 codegen backend cranelift (stage0 -> stage1, i686-pc-windows-msvc) | 0.000 | 2074 |
| 2026-09-04T11:05:47.6570305Z | 2026-09-04T11:05:47.6573390Z | Building stage1 lld-wrapper (stage0 -> stage1, i686-pc-windows-msvc) | 0.000 | 2076 |
| 2026-09-04T11:05:47.6581941Z | 2026-09-04T11:05:47.6585041Z | Building stage1 wasm-component-ld (stage0 -> stage1, i686-pc-windows-msvc) | 0.000 | 2078 |
| 2026-09-04T11:05:47.6589346Z | 2026-09-04T11:05:47.6591789Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, i686-pc-windows-msvc) | 0.000 | 2080 |
| 2026-09-04T11:05:47.6603808Z | 2026-09-04T11:05:47.6609708Z | Building stage1 library artifacts (stage1 -> stage1, i686-pc-windows-msvc) | 0.000 | 2082 |
| 2026-09-04T11:05:47.6614924Z | 2026-09-04T11:05:47.6620080Z | Building stage2 compiler artifacts (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2084 |
| 2026-09-04T11:05:47.6628291Z | 2026-09-04T11:05:47.6629283Z | Building stage2 codegen backend cranelift (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2087 |
| 2026-09-04T11:05:47.6635989Z | 2026-09-04T11:05:47.6639245Z | Building stage2 lld-wrapper (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2089 |
| 2026-09-04T11:05:47.6650459Z | 2026-09-04T11:05:47.6653734Z | Building stage2 wasm-component-ld (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2091 |
| 2026-09-04T11:05:47.6659498Z | 2026-09-04T11:05:47.6662661Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2093 |
| 2026-09-04T11:05:47.6690031Z | 2026-09-04T11:05:47.6692366Z | Building stage2 cargo (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2096 |
| 2026-09-04T11:05:47.6697948Z | 2026-09-04T11:05:47.6700733Z | Building stage2 rust-analyzer (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2098 |
| 2026-09-04T11:05:47.6706490Z | 2026-09-04T11:05:47.6709524Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2100 |
| 2026-09-04T11:05:47.6715421Z | 2026-09-04T11:05:47.6717743Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2102 |
| 2026-09-04T11:05:47.6724382Z | 2026-09-04T11:05:47.6727005Z | Building stage2 clippy-driver (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2104 |
| 2026-09-04T11:05:47.6732841Z | 2026-09-04T11:05:47.6735153Z | Building stage2 cargo-clippy (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2106 |
| 2026-09-04T11:05:47.6740620Z | 2026-09-04T11:05:47.6743551Z | Building stage2 rustfmt (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2108 |
| 2026-09-04T11:05:47.6748980Z | 2026-09-04T11:05:47.6768994Z | Building stage2 cargo-fmt (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2110 |
| 2026-09-04T11:05:47.6769763Z | 2026-09-04T11:05:47.6770649Z | Building stage2 miri (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2112 |
| 2026-09-04T11:05:47.6771399Z | 2026-09-04T11:05:47.6772236Z | Building stage2 cargo-miri (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2114 |
| 2026-09-04T11:05:47.6972770Z | 2026-09-04T11:05:47.7813130Z | Display CPU and Memory information | 0.001 | 2117 |
| 2026-09-04T11:05:47.9682922Z | 2026-09-04T11:05:48.1498919Z | Building bootstrap | 0.003 | 2237 |
| 2026-09-04T11:05:51.6757715Z | 2026-09-04T11:20:10.9388969Z | Building LLVM for i686-pc-windows-msvc | 14.321 | 2349 |
| 2026-09-04T11:20:10.9880338Z | 2026-09-04T11:42:30.4971700Z | Building stage1 compiler artifacts (stage0 -> stage1, i686-pc-windows-msvc) | 22.325 | 9532 |
| 2026-09-04T11:42:30.5139819Z | 2026-09-04T11:45:48.2982608Z | Building stage1 codegen backend cranelift (stage0 -> stage1, i686-pc-windows-msvc) | 3.296 | 10323 |
| 2026-09-04T11:45:48.3046906Z | 2026-09-04T11:46:14.1487142Z | Building LLD for i686-pc-windows-msvc | 0.431 | 10445 |
| 2026-09-04T11:46:14.1538352Z | 2026-09-04T11:46:15.2452086Z | Building stage1 lld-wrapper (stage0 -> stage1, i686-pc-windows-msvc) | 0.018 | 10686 |
| 2026-09-04T11:46:15.2528919Z | 2026-09-04T11:48:25.0477290Z | Building stage1 wasm-component-ld (stage0 -> stage1, i686-pc-windows-msvc) | 2.163 | 10695 |
| 2026-09-04T11:48:25.0512876Z | 2026-09-04T11:48:48.6922127Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, i686-pc-windows-msvc) | 0.394 | 10845 |
| 2026-09-04T11:48:48.7022422Z | 2026-09-04T11:50:33.6595836Z | Building stage1 library artifacts (stage1 -> stage1, i686-pc-windows-msvc) | 1.749 | 10926 |
| 2026-09-04T11:50:33.6609870Z | 2026-09-04T12:24:49.1148374Z | Building stage2 compiler artifacts (stage1 -> stage2, i686-pc-windows-msvc) | 34.258 | 10982 |
| 2026-09-04T12:24:49.1186314Z | 2026-09-04T12:30:24.2087727Z | Building stage2 codegen backend cranelift (stage1 -> stage2, i686-pc-windows-msvc) | 5.585 | 11586 |
| 2026-09-04T12:30:24.2109448Z | 2026-09-04T12:30:25.5957525Z | Building stage2 lld-wrapper (stage1 -> stage2, i686-pc-windows-msvc) | 0.023 | 11680 |
| 2026-09-04T12:30:25.6003640Z | 2026-09-04T12:33:16.2634763Z | Building stage2 wasm-component-ld (stage1 -> stage2, i686-pc-windows-msvc) | 2.844 | 11689 |
| 2026-09-04T12:33:16.2657367Z | 2026-09-04T12:33:54.3972329Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, i686-pc-windows-msvc) | 0.636 | 11818 |
| 2026-09-04T12:33:54.4187097Z | 2026-09-04T12:34:39.5409603Z | Building stage1 compiletest (stage0 -> stage1, i686-pc-windows-msvc) | 0.752 | 11905 |
| 2026-09-04T12:34:39.5666511Z | 2026-09-04T12:34:39.7596628Z | Building test helpers for i686-pc-windows-msvc | 0.003 | 12089 |
| 2026-09-04T12:34:39.7810181Z | 2026-09-04T13:00:07.5584656Z | Testing stage2 with compiletest suite=ui mode=ui (i686-pc-windows-msvc) | 25.463 | 12093 |
| 2026-09-04T13:00:07.5921844Z | 2026-09-04T13:00:13.6846324Z | Testing stage2 with compiletest suite=crashes mode=crashes (i686-pc-windows-msvc) | 0.102 | 34272 |
| 2026-09-04T13:00:13.7048681Z | 2026-09-04T13:00:19.2036751Z | Building stage1 coverage-dump (stage0 -> stage1, i686-pc-windows-msvc) | 0.092 | 34487 |
| 2026-09-04T13:00:19.2055580Z | 2026-09-04T13:00:26.0559806Z | Testing stage2 with compiletest suite=coverage mode=coverage-map (i686-pc-windows-msvc) | 0.114 | 34533 |
| 2026-09-04T13:00:26.0770639Z | 2026-09-04T13:00:26.2728867Z | Testing stage2 with compiletest suite=coverage mode=coverage-run (i686-pc-windows-msvc) | 0.003 | 34649 |
| 2026-09-04T13:00:26.2883830Z | 2026-09-04T13:00:49.4997524Z | Testing stage2 with compiletest suite=mir-opt mode=mir-opt (i686-pc-windows-msvc) | 0.387 | 34770 |
| 2026-09-04T13:00:49.5201335Z | 2026-09-04T13:01:37.9936067Z | Testing stage2 with compiletest suite=codegen-llvm mode=codegen (i686-pc-windows-msvc) | 0.808 | 35191 |
| 2026-09-04T13:01:38.0140645Z | 2026-09-04T13:01:40.3856410Z | Testing stage2 with compiletest suite=codegen-units mode=codegen-units (i686-pc-windows-msvc) | 0.040 | 36414 |
| 2026-09-04T13:01:40.4054894Z | 2026-09-04T13:02:29.4596624Z | Testing stage2 with compiletest suite=assembly-llvm mode=assembly (i686-pc-windows-msvc) | 0.818 | 36471 |
| 2026-09-04T13:02:29.4792681Z | 2026-09-04T13:03:05.9545889Z | Testing stage2 with compiletest suite=incremental mode=incremental (i686-pc-windows-msvc) | 0.608 | 37255 |
| 2026-09-04T13:03:07.9876657Z | 2026-09-04T13:03:52.9978073Z | Testing stage2 with compiletest suite=debuginfo mode=debuginfo (i686-pc-windows-msvc) | 0.750 | 37448 |
| 2026-09-04T13:03:53.1128063Z | 2026-09-04T13:05:02.1686185Z | Testing stage2 with compiletest suite=ui-fulldeps mode=ui (i686-pc-windows-msvc) | 1.151 | 37983 |
| 2026-09-04T13:05:02.1919936Z | 2026-09-04T13:10:24.5098481Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, i686-pc-windows-msvc) | 5.372 | 38074 |
| 2026-09-04T13:10:24.5129741Z | 2026-09-04T13:12:52.6419449Z | Testing stage2 with compiletest suite=rustdoc-html mode=rustdoc-html (i686-pc-windows-msvc) | 2.469 | 38279 |
| 2026-09-04T13:12:52.6653330Z | 2026-09-04T13:12:52.8560051Z | Testing stage2 with compiletest suite=coverage-run-rustdoc mode=coverage-run (i686-pc-windows-msvc) | 0.003 | 39093 |
| 2026-09-04T13:12:52.8770362Z | 2026-09-04T13:12:57.4476556Z | Testing stage2 with compiletest suite=pretty mode=pretty (i686-pc-windows-msvc) | 0.076 | 39107 |
| 2026-09-04T13:12:57.4746995Z | 2026-09-04T13:28:13.4263001Z | Testing stage2 {alloc, alloctests, compiler_builtins, core, coretests, panic_abort, panic_unwind, proc_macro, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} (i686-pc-windows-msvc) | 15.266 | 39238 |
| 2026-09-04T13:28:13.4318499Z | 2026-09-04T13:29:57.4455203Z | Testing stage1 tidy (i686-pc-windows-msvc) | 1.734 | 55288 |
| 2026-09-04T13:29:57.4495919Z | 2026-09-04T13:32:32.5504363Z | Building stage2 error_index_generator (stage1 -> stage2, i686-pc-windows-msvc) | 2.585 | 55597 |
| 2026-09-04T13:32:32.5620184Z | 2026-09-04T13:32:32.6586531Z | Testing stage2 error-index (i686-pc-windows-msvc) | 0.002 | 55880 |
| 2026-09-04T13:33:26.9338987Z | 2026-09-04T13:34:26.9492328Z | Testing stage1 stdarch-verify (i686-pc-windows-msvc) | 1.000 | 57010 |
| 2026-09-04T13:34:26.9539415Z | 2026-09-04T13:36:09.2955966Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage2 -> stage2, i686-pc-windows-msvc) | 1.706 | 57095 |
| 2026-09-04T13:36:09.2973105Z | 2026-09-04T13:37:05.1663174Z | Testing stage2 rustdoc-js-std (i686-pc-windows-msvc) | 0.931 | 57149 |
| 2026-09-04T13:37:05.2017978Z | 2026-09-04T13:37:30.3666200Z | Testing stage2 with compiletest suite=rustdoc-js mode=rustdoc-js (i686-pc-windows-msvc) | 0.419 | 57221 |
| 2026-09-04T13:37:30.3987866Z | 2026-09-04T13:38:15.4756966Z | Testing stage2 with compiletest suite=rustdoc-ui mode=ui (i686-pc-windows-msvc) | 0.751 | 57312 |
| 2026-09-04T13:38:15.5046827Z | 2026-09-04T13:38:50.3188793Z | Building stage1 jsondocck (stage0 -> stage1, i686-pc-windows-msvc) | 0.580 | 57771 |
| 2026-09-04T13:38:50.3212010Z | 2026-09-04T13:39:06.9664510Z | Building stage1 jsondoclint (stage0 -> stage1, i686-pc-windows-msvc) | 0.277 | 57905 |
| 2026-09-04T13:39:06.9678249Z | 2026-09-04T13:39:26.8358969Z | Testing stage2 with compiletest suite=rustdoc-json mode=rustdoc-json (i686-pc-windows-msvc) | 0.331 | 57959 |
| 2026-09-04T13:39:26.8708719Z | 2026-09-04T13:39:42.4919240Z | Building stage1 run_make_support (stage0 -> stage1, i686-pc-windows-msvc) | 0.260 | 58166 |
| 2026-09-04T13:39:42.4937773Z | 2026-09-04T13:44:20.2924046Z | Testing stage2 with compiletest suite=run-make mode=run-make (i686-pc-windows-msvc) | 4.630 | 58249 |
| 2026-09-04T13:44:20.3344322Z | 2026-09-04T14:00:16.7229188Z | Building stage2 cargo (stage1 -> stage2, i686-pc-windows-msvc) | 15.940 | 58787 |
| 2026-09-04T14:00:16.7248979Z | 2026-09-04T14:05:56.5527723Z | Testing stage2 with compiletest suite=run-make-cargo mode=run-make (i686-pc-windows-msvc) | 5.664 | 59723 |
| 2026-09-04T14:05:56.7324315Z | 2026-09-04T14:05:56.7686911Z | sccache stats | 0.001 | 59755 |

</details>

## [auto - aarch64-msvc-2: 100999917959](https://github.com/rust-lang/rust/actions/runs/33865610474/job/100999917959)

Run 33865610474; raw SHA256 `82b5fe3213a8eae664aefe5d1bcdc6838325d0307dc4fa9b77fbafb8c2cfc7bb`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 7.453 |
| Build support | 1.135 |
| LLVM/LLD | 12.237 |
| Compiler | 30.207 |
| Tools | 10.731 |
| Libraries | 1.333 |
| Tests | 27.610 |
| Docs | 3.445 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-04T11:08:38.8963142Z | 2026-09-04T11:08:38.8999205Z | Run set +e | 0.000 | 1800 |
| 2026-09-04T11:08:41.8736470Z | 2026-09-04T11:08:42.1872236Z | Clock drift check | 0.005 | 1846 |
| 2026-09-04T11:08:44.4175942Z | 2026-09-04T11:08:44.4196017Z | Configure the build | 0.000 | 1852 |
| 2026-09-04T11:08:53.7716809Z | 2026-09-04T11:10:01.0987690Z | Building bootstrap | 1.122 | 1897 |
| 2026-09-04T11:10:02.8587514Z | 2026-09-04T11:10:02.8682055Z | Building LLVM for aarch64-pc-windows-msvc | 0.000 | 2077 |
| 2026-09-04T11:10:02.8718769Z | 2026-09-04T11:10:02.8729838Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2079 |
| 2026-09-04T11:10:02.8737691Z | 2026-09-04T11:10:02.8738384Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2082 |
| 2026-09-04T11:10:02.8747069Z | 2026-09-04T11:10:02.8769602Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2084 |
| 2026-09-04T11:10:02.8781394Z | 2026-09-04T11:10:02.8783809Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2086 |
| 2026-09-04T11:10:02.8788830Z | 2026-09-04T11:10:02.8791534Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2088 |
| 2026-09-04T11:10:02.8808463Z | 2026-09-04T11:10:02.8814075Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2090 |
| 2026-09-04T11:10:02.8819511Z | 2026-09-04T11:10:02.8823895Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2092 |
| 2026-09-04T11:10:02.8830774Z | 2026-09-04T11:10:02.8831435Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2095 |
| 2026-09-04T11:10:02.8837808Z | 2026-09-04T11:10:02.8841119Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2097 |
| 2026-09-04T11:10:02.8851709Z | 2026-09-04T11:10:02.8854493Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2099 |
| 2026-09-04T11:10:02.8859045Z | 2026-09-04T11:10:02.8861493Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2101 |
| 2026-09-04T11:10:02.8884759Z | 2026-09-04T11:10:02.8887365Z | Building stage2 cargo (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2104 |
| 2026-09-04T11:10:02.8892133Z | 2026-09-04T11:10:02.8894652Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2106 |
| 2026-09-04T11:10:02.8899540Z | 2026-09-04T11:10:02.8902024Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2108 |
| 2026-09-04T11:10:02.8909332Z | 2026-09-04T11:10:02.8911951Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2110 |
| 2026-09-04T11:10:02.8918658Z | 2026-09-04T11:10:02.8921224Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2112 |
| 2026-09-04T11:10:02.8927195Z | 2026-09-04T11:10:02.8929741Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2114 |
| 2026-09-04T11:10:02.8935904Z | 2026-09-04T11:10:02.8938567Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2116 |
| 2026-09-04T11:10:02.8944502Z | 2026-09-04T11:10:02.8947366Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2118 |
| 2026-09-04T11:10:02.8953611Z | 2026-09-04T11:10:02.8956408Z | Building stage2 miri (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2120 |
| 2026-09-04T11:10:02.8962970Z | 2026-09-04T11:10:02.8965941Z | Building stage2 cargo-miri (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2122 |
| 2026-09-04T11:10:02.9228084Z | 2026-09-04T11:10:03.1841288Z | Display CPU and Memory information | 0.004 | 2125 |
| 2026-09-04T11:10:07.3144919Z | 2026-09-04T11:10:07.5095474Z | Building bootstrap | 0.003 | 2233 |
| 2026-09-04T11:10:09.2911488Z | 2026-09-04T11:11:07.9509314Z | Building stage1 tidy (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.978 | 2247 |
| 2026-09-04T11:15:51.0043533Z | 2026-09-04T11:27:36.3447750Z | Building LLVM for aarch64-pc-windows-msvc | 11.756 | 3188 |
| 2026-09-04T11:27:36.5032620Z | 2026-09-04T11:39:21.9017290Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 11.757 | 10360 |
| 2026-09-04T11:39:21.9228479Z | 2026-09-04T11:41:26.0281050Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-pc-windows-msvc) | 2.068 | 10964 |
| 2026-09-04T11:41:26.0482644Z | 2026-09-04T11:41:54.8983968Z | Building LLD for aarch64-pc-windows-msvc | 0.481 | 11058 |
| 2026-09-04T11:41:57.1134273Z | 2026-09-04T11:41:58.3061990Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.020 | 11299 |
| 2026-09-04T11:41:58.3229426Z | 2026-09-04T11:42:55.0899381Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.946 | 11308 |
| 2026-09-04T11:42:55.0976335Z | 2026-09-04T11:43:08.8726199Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.230 | 11417 |
| 2026-09-04T11:43:08.9082958Z | 2026-09-04T11:44:28.5018390Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 1.327 | 11500 |
| 2026-09-04T11:44:28.5472925Z | 2026-09-04T12:02:55.5806921Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 18.451 | 11555 |
| 2026-09-04T12:02:55.5859866Z | 2026-09-04T12:05:49.8321023Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-pc-windows-msvc) | 2.904 | 12159 |
| 2026-09-04T12:05:49.8350604Z | 2026-09-04T12:05:51.1568200Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.022 | 12253 |
| 2026-09-04T12:05:51.1659001Z | 2026-09-04T12:07:21.0258691Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.498 | 12262 |
| 2026-09-04T12:07:21.0289057Z | 2026-09-04T12:07:42.6614293Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.361 | 12391 |
| 2026-09-04T12:07:42.6816250Z | 2026-09-04T12:07:43.0548849Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.006 | 12484 |
| 2026-09-04T12:07:43.0583253Z | 2026-09-04T12:09:21.9887669Z | Building stage1 rustdoc-tool-binary (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.649 | 12518 |
| 2026-09-04T12:09:21.9971170Z | 2026-09-04T12:14:22.6160801Z | Testing stage2 {rustc-main, rustc_abi, rustc_arena, rustc_ast, rustc_ast_ir, rustc_ast_lowering, rustc_ast_passes, rustc_ast_pretty, rustc_attr_ir, rustc_attr_parsing, rustc_baked_icu_data, rustc_borrowck, rustc_builtin_macros, rustc_codegen_llvm, rustc_codegen_ssa, rustc_const_eval, rustc_crate_store, rustc_data_structures, rustc_driver, rustc_driver_impl, rustc_error_codes, rustc_error_messages, rustc_errors, rustc_expand, rustc_feature, rustc_fs_util, rustc_graphviz, rustc_hashes, rustc_hir, rustc_hir_analysis, rustc_hir_id, rustc_hir_pretty, rustc_hir_typeck, rustc_incremental, rustc_index, rustc_index_macros, rustc_infer, rustc_interface, rustc_lexer, rustc_lint, rustc_lint_defs, rustc_llvm, rustc_log, rustc_macros, rustc_metadata, rustc_middle, rustc_mir_build, rustc_mir_dataflow, rustc_mir_transform, rustc_monomorphize, rustc_next_trait_solver, rustc_parse, rustc_parse_format, rustc_passes, rustc_pattern_analysis, rustc_privacy, rustc_proc_macro, rustc_public, rustc_public_bridge, rustc_query_impl, rustc_resolve, rustc_sanitizers, rustc_serialize, rustc_session, rustc_span, rustc_structures, rustc_symbol_mangling, rustc_target, rustc_thread_pool, rustc_trait_selection, rustc_traits, rustc_transmute, rustc_ty_utils, rustc_ty_walk, rustc_type_ir, rustc_type_ir_macros, rustc_windows_rc} (aarch64-pc-windows-msvc) | 5.010 | 12704 |
| 2026-09-04T12:14:22.6321292Z | 2026-09-04T12:17:17.0924543Z | Testing stage2 rustdoc (aarch64-pc-windows-msvc) | 2.908 | 16080 |
| 2026-09-04T12:17:17.0993425Z | 2026-09-04T12:17:56.5849382Z | Testing stage2 rustdoc-json-types (aarch64-pc-windows-msvc) | 0.658 | 16432 |
| 2026-09-04T12:17:56.5879579Z | 2026-09-04T12:18:08.1968757Z | Testing stage1 coverage-dump (aarch64-pc-windows-msvc) | 0.193 | 16558 |
| 2026-09-04T12:18:08.1982790Z | 2026-09-04T12:18:20.6659008Z | Testing stage1 jsondoclint (aarch64-pc-windows-msvc) | 0.208 | 16617 |
| 2026-09-04T12:18:20.6683625Z | 2026-09-04T12:18:22.3189231Z | Testing stage1 replace-version-placeholder (aarch64-pc-windows-msvc) | 0.028 | 16690 |
| 2026-09-04T12:18:22.3211596Z | 2026-09-04T12:18:31.9516489Z | Testing stage1 remote-test-client (aarch64-pc-windows-msvc) | 0.161 | 16826 |
| 2026-09-04T12:18:31.9530762Z | 2026-09-04T12:18:33.1134148Z | Testing stage2 platform support check (aarch64-pc-windows-msvc) | 0.019 | 16872 |
| 2026-09-04T12:18:33.1308512Z | 2026-09-04T12:35:31.6555696Z | Testing stage2 rust-analyzer (aarch64-pc-windows-msvc) | 16.975 | 16880 |
| 2026-09-04T12:35:31.6647350Z | 2026-09-04T12:36:53.8940790Z | Building stage2 error_index_generator (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.370 | 26163 |
| 2026-09-04T12:36:53.8955648Z | 2026-09-04T12:36:53.9438983Z | Testing stage2 error-index (aarch64-pc-windows-msvc) | 0.001 | 26368 |
| 2026-09-04T12:36:53.9791506Z | 2026-09-04T12:36:55.8741066Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.032 | 26379 |
| 2026-09-04T12:37:45.5394062Z | 2026-09-04T12:37:52.1345441Z | Testing stage2 book rustdoc (aarch64-pc-windows-msvc) | 0.110 | 27611 |
| 2026-09-04T12:37:52.1369118Z | 2026-09-04T12:38:11.9158422Z | Testing stage2 book unstable-book (aarch64-pc-windows-msvc) | 0.330 | 27815 |
| 2026-09-04T12:38:11.9166537Z | 2026-09-04T12:38:21.4626648Z | Testing stage2 book rustc (aarch64-pc-windows-msvc) | 0.159 | 28409 |
| 2026-09-04T12:38:21.5578900Z | 2026-09-04T12:38:25.1234264Z | Building stage1 lint-docs (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.059 | 29058 |
| 2026-09-04T12:38:25.1743110Z | 2026-09-04T12:38:56.8764103Z | Running stage2 lint-docs (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.528 | 29088 |
| 2026-09-04T12:38:56.8791518Z | 2026-09-04T12:40:06.2942435Z | Building stage1 rustbook (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.157 | 29093 |
| 2026-09-04T12:40:07.2303503Z | 2026-09-04T12:40:08.6709483Z | Building stage1 rustdoc-themes (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.024 | 29443 |
| 2026-09-04T12:40:08.8078973Z | 2026-09-04T12:40:34.1496599Z | Testing stage1 rust-installer (aarch64-pc-windows-msvc) | 0.422 | 29458 |
| 2026-09-04T12:40:34.1518947Z | 2026-09-04T12:41:19.6310119Z | Testing stage3 test-float-parse (aarch64-pc-windows-msvc) | 0.758 | 29555 |

</details>

## [auto - dist-aarch64-msvc: 100999918026](https://github.com/rust-lang/rust/actions/runs/33865610474/job/100999918026)

Run 33865610474; raw SHA256 `f2cd5b808408ede7906f49f476d55a34e8bfeb6b64687520b3badad2de53f346`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 5.528 |
| Build support | 5.135 |
| LLVM/LLD | 11.940 |
| Compiler | 21.241 |
| Tools | 24.707 |
| Libraries | 1.753 |
| Docs | 9.272 |
| Packaging | 24.641 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-04T11:10:14.0654884Z | 2026-09-04T11:10:14.0693604Z | Run set +e | 0.000 | 1855 |
| 2026-09-04T11:10:16.8108776Z | 2026-09-04T11:10:17.1278003Z | Clock drift check | 0.005 | 1903 |
| 2026-09-04T11:10:18.9689412Z | 2026-09-04T11:10:18.9711026Z | Configure the build | 0.000 | 1909 |
| 2026-09-04T11:10:29.0431846Z | 2026-09-04T11:11:38.9230158Z | Building bootstrap | 1.165 | 1954 |
| 2026-09-04T11:11:40.5593918Z | 2026-09-04T11:11:40.5681156Z | Building LLVM for aarch64-pc-windows-msvc | 0.000 | 2134 |
| 2026-09-04T11:11:40.5717177Z | 2026-09-04T11:11:40.5728116Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2136 |
| 2026-09-04T11:11:40.5739264Z | 2026-09-04T11:11:40.5762727Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2139 |
| 2026-09-04T11:11:40.5774868Z | 2026-09-04T11:11:40.5778107Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2141 |
| 2026-09-04T11:11:40.5782894Z | 2026-09-04T11:11:40.5785707Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2143 |
| 2026-09-04T11:11:40.5803377Z | 2026-09-04T11:11:40.5808144Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2145 |
| 2026-09-04T11:11:40.5813713Z | 2026-09-04T11:11:40.5818078Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2147 |
| 2026-09-04T11:11:40.5825016Z | 2026-09-04T11:11:40.5828511Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2150 |
| 2026-09-04T11:11:40.5838357Z | 2026-09-04T11:11:40.5841362Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2152 |
| 2026-09-04T11:11:40.5845103Z | 2026-09-04T11:11:40.5847716Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2154 |
| 2026-09-04T11:11:40.5897193Z | 2026-09-04T11:11:40.5903034Z | Building stage1 library artifacts (stage1:aarch64-pc-windows-msvc -> stage1:arm64ec-pc-windows-msvc) | 0.000 | 2157 |
| 2026-09-04T11:11:40.5944583Z | 2026-09-04T11:11:40.5947834Z | Building stage2 cargo (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2160 |
| 2026-09-04T11:11:40.5952429Z | 2026-09-04T11:11:40.5955235Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2162 |
| 2026-09-04T11:11:40.5960045Z | 2026-09-04T11:11:40.5962917Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2164 |
| 2026-09-04T11:11:40.5970231Z | 2026-09-04T11:11:40.5973140Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2166 |
| 2026-09-04T11:11:40.5979978Z | 2026-09-04T11:11:40.5982646Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2168 |
| 2026-09-04T11:11:40.5988394Z | 2026-09-04T11:11:40.5991178Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2170 |
| 2026-09-04T11:11:40.5997059Z | 2026-09-04T11:11:40.5999703Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2172 |
| 2026-09-04T11:11:40.6005185Z | 2026-09-04T11:11:40.6008326Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2174 |
| 2026-09-04T11:11:40.6014096Z | 2026-09-04T11:11:40.6016851Z | Building stage2 miri (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2176 |
| 2026-09-04T11:11:40.6022936Z | 2026-09-04T11:11:40.6025563Z | Building stage2 cargo-miri (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2178 |
| 2026-09-04T11:11:40.6340283Z | 2026-09-04T11:11:40.9929909Z | Display CPU and Memory information | 0.006 | 2181 |
| 2026-09-04T11:11:41.2391934Z | 2026-09-04T11:11:41.4277692Z | Building bootstrap | 0.003 | 2289 |
| 2026-09-04T11:11:43.7285980Z | 2026-09-04T11:23:15.2359352Z | Building LLVM for aarch64-pc-windows-msvc | 11.525 | 2301 |
| 2026-09-04T11:23:16.2541615Z | 2026-09-04T11:34:01.3938377Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 10.752 | 9477 |
| 2026-09-04T11:34:01.4145757Z | 2026-09-04T11:34:26.3103564Z | Building LLD for aarch64-pc-windows-msvc | 0.415 | 10269 |
| 2026-09-04T11:34:26.3133361Z | 2026-09-04T11:34:29.5696991Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.054 | 10508 |
| 2026-09-04T11:34:30.8026581Z | 2026-09-04T11:35:30.5133094Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.995 | 10517 |
| 2026-09-04T11:35:30.5210447Z | 2026-09-04T11:35:44.0116776Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.225 | 10667 |
| 2026-09-04T11:35:44.0354630Z | 2026-09-04T11:36:37.8709027Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.897 | 10747 |
| 2026-09-04T11:36:37.8781550Z | 2026-09-04T11:37:27.5741470Z | Building stage1 unstable-book-gen (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.828 | 10811 |
| 2026-09-04T11:37:29.0297821Z | 2026-09-04T11:38:39.1233892Z | Building stage1 rustbook (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.168 | 11066 |
| 2026-09-04T11:38:42.5886193Z | 2026-09-04T11:39:33.9225092Z | Building stage1 library artifacts (stage1:aarch64-pc-windows-msvc -> stage1:arm64ec-pc-windows-msvc) | 0.856 | 11506 |
| 2026-09-04T11:39:40.8346053Z | 2026-09-04T11:39:40.8495607Z | Documenting stage2 book redirect pages (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 11601 |
| 2026-09-04T11:39:40.8496393Z | 2026-09-04T11:41:19.5770202Z | Building stage1 rustdoc-tool-binary (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.645 | 11605 |
| 2026-09-04T11:41:19.5773942Z | 2026-09-04T11:41:22.7671620Z | Documenting stage2 book redirect pages (stage1 -> stage2, aarch64-pc-windows-msvc) (continued) | 0.053 | 11808 |
| 2026-09-04T11:41:24.2944413Z | 2026-09-04T11:41:27.4563916Z | Documenting stage2 book redirect pages (stage1:aarch64-pc-windows-msvc -> stage2:arm64ec-pc-windows-msvc) | 0.053 | 11841 |
| 2026-09-04T11:41:27.4587612Z | 2026-09-04T11:41:28.6819045Z | Documenting stage2 standalone (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.020 | 11845 |
| 2026-09-04T11:41:28.6831266Z | 2026-09-04T11:41:29.8852317Z | Documenting stage2 standalone (stage1:aarch64-pc-windows-msvc -> stage2:arm64ec-pc-windows-msvc) | 0.020 | 11849 |
| 2026-09-04T11:41:29.8918782Z | 2026-09-04T11:43:45.6885603Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage1 -> stage1, aarch64-pc-windows-msvc) | 2.263 | 11853 |
| 2026-09-04T11:43:45.7007385Z | 2026-09-04T11:46:00.3713200Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage1:aarch64-pc-windows-msvc -> stage1:arm64ec-pc-windows-msvc) | 2.245 | 11908 |
| 2026-09-04T11:46:00.3871539Z | 2026-09-04T11:56:29.6808884Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 10.488 | 11968 |
| 2026-09-04T11:56:29.6858249Z | 2026-09-04T11:56:30.7537986Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.018 | 12573 |
| 2026-09-04T11:56:30.7633633Z | 2026-09-04T11:57:30.5690686Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.997 | 12582 |
| 2026-09-04T11:57:30.5716026Z | 2026-09-04T11:57:44.5381880Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.233 | 12711 |
| 2026-09-04T11:57:44.5441729Z | 2026-09-04T11:58:39.0122176Z | Building stage2 error_index_generator (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.908 | 12789 |
| 2026-09-04T11:59:06.2040562Z | 2026-09-04T11:59:11.2588876Z | Building stage1 lint-docs (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.084 | 13229 |
| 2026-09-04T11:59:11.3091037Z | 2026-09-04T11:59:40.1666447Z | Running stage2 lint-docs (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.481 | 13260 |
| 2026-09-04T11:59:44.4358799Z | 2026-09-04T11:59:44.6835989Z | Documenting stage2 releases (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.004 | 13363 |
| 2026-09-04T11:59:44.6841819Z | 2026-09-04T11:59:44.9121804Z | Documenting stage2 releases (stage1:aarch64-pc-windows-msvc -> stage2:arm64ec-pc-windows-msvc) | 0.004 | 13367 |
| 2026-09-04T12:00:26.0280728Z | 2026-09-04T12:00:52.4119498Z | Building stage1 rust-installer (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.440 | 13372 |
| 2026-09-04T12:05:26.0729606Z | 2026-09-04T12:05:42.8080030Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.279 | 13463 |
| 2026-09-04T12:05:50.7372890Z | 2026-09-04T12:06:05.9066117Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage1:aarch64-pc-windows-msvc -> stage1:arm64ec-pc-windows-msvc) | 0.253 | 13502 |
| 2026-09-04T12:06:13.4052554Z | 2026-09-04T12:07:57.9453743Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.742 | 13546 |
| 2026-09-04T12:07:57.9570401Z | 2026-09-04T12:08:48.6189533Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.844 | 13725 |
| 2026-09-04T12:08:48.6997903Z | 2026-09-04T12:12:38.4365017Z | Vendoring sources to "C:\\a\\rust\\rust" | 3.829 | 13923 |
| 2026-09-04T12:12:38.4389292Z | 2026-09-04T12:12:38.4410259Z | generate-copyright | 0.000 | 16518 |
| 2026-09-04T12:12:38.4410820Z | 2026-09-04T12:13:20.2622952Z | Building stage1 generate-copyright (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.697 | 16522 |
| 2026-09-04T12:13:20.2626309Z | 2026-09-04T12:13:25.6947104Z | generate-copyright (continued) | 0.091 | 16667 |
| 2026-09-04T12:16:24.6852048Z | 2026-09-04T12:16:26.7134253Z | Vendoring sources to "C:\\a\\rust\\rust\\build\\tmp\\tarball\\rust-src\\image\\lib/rustlib/src/rust" | 0.034 | 21061 |
| 2026-09-04T12:16:40.6126031Z | 2026-09-04T12:23:02.6675280Z | Building stage2 cargo (stage1 -> stage2, aarch64-pc-windows-msvc) | 6.368 | 21103 |
| 2026-09-04T12:23:13.9899482Z | 2026-09-04T12:29:04.4162635Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-pc-windows-msvc) | 5.840 | 21824 |
| 2026-09-04T12:29:15.5755245Z | 2026-09-04T12:30:19.9005349Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.072 | 22322 |
| 2026-09-04T12:30:19.9039831Z | 2026-09-04T12:30:20.4981511Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.010 | 22495 |
| 2026-09-04T12:30:25.6586414Z | 2026-09-04T12:32:26.2624393Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-pc-windows-msvc) | 2.010 | 22609 |
| 2026-09-04T12:32:26.2709810Z | 2026-09-04T12:32:26.8872451Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.010 | 22777 |
| 2026-09-04T12:32:34.6523481Z | 2026-09-04T12:33:53.8912777Z | Building stage2 miri (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.321 | 22888 |
| 2026-09-04T12:33:53.8988743Z | 2026-09-04T12:34:05.0203880Z | Building stage2 cargo-miri (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.185 | 23080 |
| 2026-09-04T12:39:53.4386009Z | 2026-09-04T12:40:29.9310988Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage2 -> stage2, aarch64-pc-windows-msvc) | 0.608 | 23177 |
| 2026-09-04T12:54:26.5003599Z | 2026-09-04T12:54:26.6430379Z | sccache stats | 0.002 | 23260 |
| 2026-09-04T12:00:52.4659907Z | 2026-09-04T12:02:45.0340129Z | Dist rust-docs-nightly-aarch64-pc-windows-msvc | 1.876 | 13454 |
| 2026-09-04T12:03:34.2838766Z | 2026-09-04T12:05:26.0667845Z | Dist rust-docs-nightly-arm64ec-pc-windows-msvc | 1.863 | 13458 |
| 2026-09-04T12:05:42.8850651Z | 2026-09-04T12:05:50.7330463Z | Dist rust-docs-json-nightly-aarch64-pc-windows-msvc | 0.131 | 13497 |
| 2026-09-04T12:06:05.9935100Z | 2026-09-04T12:06:13.3919319Z | Dist rust-docs-json-nightly-arm64ec-pc-windows-msvc | 0.123 | 13536 |
| 2026-09-04T12:13:25.7906036Z | 2026-09-04T12:14:20.2447782Z | Dist rustc-nightly-aarch64-pc-windows-msvc | 0.908 | 21036 |
| 2026-09-04T12:14:20.3649017Z | 2026-09-04T12:14:34.0360807Z | Dist rust-std-nightly-aarch64-pc-windows-msvc | 0.228 | 21040 |
| 2026-09-04T12:14:34.1506354Z | 2026-09-04T12:14:47.4245923Z | Dist rust-std-nightly-arm64ec-pc-windows-msvc | 0.221 | 21044 |
| 2026-09-04T12:14:51.7396268Z | 2026-09-04T12:16:21.1927589Z | Dist rustc-dev-nightly-aarch64-pc-windows-msvc | 1.491 | 21048 |
| 2026-09-04T12:16:21.3481802Z | 2026-09-04T12:16:21.4054987Z | Dist rust-analysis-nightly-aarch64-pc-windows-msvc | 0.001 | 21052 |
| 2026-09-04T12:16:21.4873703Z | 2026-09-04T12:16:21.5439889Z | Dist rust-analysis-nightly-arm64ec-pc-windows-msvc | 0.001 | 21056 |
| 2026-09-04T12:16:26.7839586Z | 2026-09-04T12:16:40.6095927Z | Dist rust-src-nightly | 0.230 | 21097 |
| 2026-09-04T12:23:02.7809016Z | 2026-09-04T12:23:13.9809131Z | Dist cargo-nightly-aarch64-pc-windows-msvc | 0.187 | 21818 |
| 2026-09-04T12:29:04.4973365Z | 2026-09-04T12:29:15.5705050Z | Dist rust-analyzer-nightly-aarch64-pc-windows-msvc | 0.185 | 22316 |
| 2026-09-04T12:30:20.5753301Z | 2026-09-04T12:30:25.6564154Z | Dist rustfmt-nightly-aarch64-pc-windows-msvc | 0.085 | 22603 |
| 2026-09-04T12:32:26.9690505Z | 2026-09-04T12:32:34.6497031Z | Dist clippy-nightly-aarch64-pc-windows-msvc | 0.128 | 22882 |
| 2026-09-04T12:34:05.0960279Z | 2026-09-04T12:34:09.6919157Z | Dist miri-nightly-aarch64-pc-windows-msvc | 0.077 | 23156 |
| 2026-09-04T12:34:09.7854191Z | 2026-09-04T12:34:50.4708460Z | Dist llvm-tools-nightly-aarch64-pc-windows-msvc | 0.678 | 23160 |
| 2026-09-04T12:34:50.5592089Z | 2026-09-04T12:34:52.0427799Z | Dist llvm-bitcode-linker-nightly-aarch64-pc-windows-msvc | 0.025 | 23164 |
| 2026-09-04T12:34:54.7766164Z | 2026-09-04T12:39:53.4210348Z | Dist rust-dev-nightly-aarch64-pc-windows-msvc | 4.977 | 23170 |
| 2026-09-04T12:40:30.0297838Z | 2026-09-04T12:40:38.1181775Z | Dist rust-docs-json-nightly-aarch64-pc-windows-msvc | 0.135 | 23232 |
| 2026-09-04T12:40:38.1980277Z | 2026-09-04T12:46:17.0797925Z | Dist rust-nightly-aarch64-pc-windows-msvc | 5.648 | 23235 |
| 2026-09-04T12:48:59.3032031Z | 2026-09-04T12:54:18.3344136Z | MSI package | 5.317 | 23249 |
| 2026-09-04T12:54:18.5255711Z | 2026-09-04T12:54:26.1517281Z | Dist bootstrap-nightly-aarch64-pc-windows-msvc | 0.127 | 23256 |

</details>

## [auto - dist-x86_64-msvc: 100999918111](https://github.com/rust-lang/rust/actions/runs/33865610474/job/100999918111)

Run 33865610474; raw SHA256 `de0616cd75dfb914075ee8e48b21fd9fb5c9e3fd9916ef37e32b9344d96f1f2c`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 5.010 |
| Build support | 4.820 |
| LLVM/LLD | 23.537 |
| Compiler | 24.908 |
| Tools | 58.694 |
| Libraries | 0.979 |
| Tests | 32.904 |
| Docs | 4.847 |
| Packaging | 16.319 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-04T11:05:38.6037736Z | 2026-09-04T11:05:38.6067889Z | Run set +e | 0.000 | 1867 |
| 2026-09-04T11:05:40.6522471Z | 2026-09-04T11:05:40.8348979Z | Clock drift check | 0.003 | 1916 |
| 2026-09-04T11:05:42.2981160Z | 2026-09-04T11:05:42.2999393Z | Configure the build | 0.000 | 1922 |
| 2026-09-04T11:05:53.9905650Z | 2026-09-04T11:06:40.3460559Z | Building bootstrap | 0.773 | 1968 |
| 2026-09-04T11:06:41.9964641Z | 2026-09-04T11:06:42.0037972Z | Building LLVM for x86_64-pc-windows-msvc | 0.000 | 2148 |
| 2026-09-04T11:06:42.0068039Z | 2026-09-04T11:06:42.0076825Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2150 |
| 2026-09-04T11:06:42.0083363Z | 2026-09-04T11:06:42.0083951Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2153 |
| 2026-09-04T11:06:42.0091268Z | 2026-09-04T11:06:42.0097333Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2155 |
| 2026-09-04T11:06:42.0106894Z | 2026-09-04T11:06:42.0108402Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2157 |
| 2026-09-04T11:06:42.0112269Z | 2026-09-04T11:06:42.0114606Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2159 |
| 2026-09-04T11:06:42.0128516Z | 2026-09-04T11:06:42.0133748Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2161 |
| 2026-09-04T11:06:42.0137420Z | 2026-09-04T11:06:42.0141282Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2163 |
| 2026-09-04T11:06:42.0146932Z | 2026-09-04T11:06:42.0147490Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2166 |
| 2026-09-04T11:06:42.0153347Z | 2026-09-04T11:06:42.0156260Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2168 |
| 2026-09-04T11:06:42.0164801Z | 2026-09-04T11:06:42.0166946Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2170 |
| 2026-09-04T11:06:42.0170769Z | 2026-09-04T11:06:42.0172971Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2172 |
| 2026-09-04T11:06:42.0191780Z | 2026-09-04T11:06:42.0194029Z | Building stage2 cargo (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2175 |
| 2026-09-04T11:06:42.0198218Z | 2026-09-04T11:06:42.0200264Z | Building stage2 rust-analyzer (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2177 |
| 2026-09-04T11:06:42.0204360Z | 2026-09-04T11:06:42.0206310Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2179 |
| 2026-09-04T11:06:42.0212921Z | 2026-09-04T11:06:42.0214967Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2181 |
| 2026-09-04T11:06:42.0220439Z | 2026-09-04T11:06:42.0222488Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2183 |
| 2026-09-04T11:06:42.0227006Z | 2026-09-04T11:06:42.0229058Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2185 |
| 2026-09-04T11:06:42.0234639Z | 2026-09-04T11:06:42.0236995Z | Building stage2 rustfmt (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2187 |
| 2026-09-04T11:06:42.0241614Z | 2026-09-04T11:06:42.0243656Z | Building stage2 cargo-fmt (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2189 |
| 2026-09-04T11:06:42.0248570Z | 2026-09-04T11:06:42.0250527Z | Building stage2 miri (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2191 |
| 2026-09-04T11:06:42.0256322Z | 2026-09-04T11:06:42.0258490Z | Building stage2 cargo-miri (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2193 |
| 2026-09-04T11:06:42.0461942Z | 2026-09-04T11:06:42.1263007Z | Display CPU and Memory information | 0.001 | 2196 |
| 2026-09-04T11:06:42.3567454Z | 2026-09-04T11:06:42.5034934Z | Building bootstrap | 0.002 | 2424 |
| 2026-09-04T11:06:43.2704896Z | 2026-09-04T11:07:26.8168008Z | Building stage1 opt-dist (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.726 | 2437 |
| 2026-09-04T11:07:26.8490345Z | 2026-09-04T11:07:26.8577607Z | Environment values | 0.000 | 2692 |
| 2026-09-04T11:07:26.8577961Z | 2026-09-04T11:07:26.8642689Z | Printing bootstrap.toml | 0.000 | 2877 |
| 2026-09-04T11:07:26.8643712Z | 2026-09-04T11:09:28.0767545Z | Building rustc-perf | 2.020 | 3070 |
| 2026-09-04T11:09:28.1888909Z | 2026-09-04T11:09:28.3433686Z | Building bootstrap | 0.003 | 3646 |
| 2026-09-04T11:09:29.2768884Z | 2026-09-04T11:16:46.2557553Z | Building LLVM for x86_64-pc-windows-msvc | 7.283 | 3657 |
| 2026-09-04T11:16:46.3143452Z | 2026-09-04T11:24:34.9552115Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-pc-windows-msvc) | 7.811 | 10849 |
| 2026-09-04T11:24:34.9655274Z | 2026-09-04T11:28:43.0464616Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-pc-windows-msvc) | 4.135 | 11570 |
| 2026-09-04T11:28:43.0484359Z | 2026-09-04T11:29:00.3032248Z | Building LLD for x86_64-pc-windows-msvc | 0.288 | 11689 |
| 2026-09-04T11:29:00.3042337Z | 2026-09-04T11:29:01.0953203Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.013 | 11928 |
| 2026-09-04T11:29:01.1028679Z | 2026-09-04T11:29:50.7397738Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.827 | 11937 |
| 2026-09-04T11:29:50.7426202Z | 2026-09-04T11:30:07.1125025Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.273 | 12079 |
| 2026-09-04T11:30:07.1182365Z | 2026-09-04T11:31:04.8486475Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-pc-windows-msvc) | 0.962 | 12160 |
| 2026-09-04T11:31:04.8500070Z | 2026-09-04T11:38:23.8532530Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-pc-windows-msvc) | 7.317 | 12219 |
| 2026-09-04T11:38:23.8576930Z | 2026-09-04T11:42:57.0904249Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-pc-windows-msvc) | 4.554 | 12823 |
| 2026-09-04T11:42:57.0991070Z | 2026-09-04T11:42:57.9264241Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.014 | 12917 |
| 2026-09-04T11:42:57.9340447Z | 2026-09-04T11:43:54.5894334Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.944 | 12926 |
| 2026-09-04T11:43:54.5920151Z | 2026-09-04T11:44:12.3843802Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.297 | 13055 |
| 2026-09-04T11:44:12.4133136Z | 2026-09-04T11:47:03.2527572Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, x86_64-pc-windows-msvc) | 2.847 | 13138 |
| 2026-09-04T11:47:03.2559217Z | 2026-09-04T11:55:00.8350141Z | Building stage2 cargo (stage1 -> stage2, x86_64-pc-windows-msvc) | 7.960 | 13344 |
| 2026-09-04T11:55:00.8367146Z | 2026-09-04T11:58:29.3439998Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-pc-windows-msvc) | 3.475 | 14225 |
| 2026-09-04T11:58:29.3465284Z | 2026-09-04T11:58:29.8185679Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.008 | 14416 |
| 2026-09-04T11:58:29.8452024Z | 2026-09-04T12:11:38.8838129Z | Running benchmarks | 13.151 | 14573 |
| 2026-09-04T12:12:25.0486120Z | 2026-09-04T12:14:06.3698208Z | Running benchmarks | 1.689 | 14646 |
| 2026-09-04T12:14:25.5911121Z | 2026-09-04T12:16:55.5771457Z | Running benchmarks | 2.500 | 14700 |
| 2026-09-04T12:17:16.9428253Z | 2026-09-04T12:17:17.1784695Z | Building bootstrap | 0.004 | 14756 |
| 2026-09-04T12:17:18.4571639Z | 2026-09-04T12:17:19.9926043Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.026 | 14782 |
| 2026-09-04T12:17:20.0021929Z | 2026-09-04T12:17:20.3322526Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.006 | 15111 |
| 2026-09-04T12:17:20.3345669Z | 2026-09-04T12:17:20.6799041Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.006 | 15168 |
| 2026-09-04T12:17:20.6872259Z | 2026-09-04T12:17:21.1146319Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.007 | 15176 |
| 2026-09-04T12:17:21.1172703Z | 2026-09-04T12:17:21.4814372Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.006 | 15248 |
| 2026-09-04T12:17:21.4868171Z | 2026-09-04T12:17:21.9768097Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-pc-windows-msvc) | 0.008 | 15302 |
| 2026-09-04T12:17:21.9777304Z | 2026-09-04T12:25:43.4896858Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-pc-windows-msvc) | 8.359 | 15336 |
| 2026-09-04T12:25:43.4933677Z | 2026-09-04T12:26:11.6638549Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.470 | 15907 |
| 2026-09-04T12:26:11.6659312Z | 2026-09-04T12:26:11.9789135Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.005 | 15963 |
| 2026-09-04T12:26:11.9864695Z | 2026-09-04T12:26:12.4212491Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.007 | 15971 |
| 2026-09-04T12:26:12.4240538Z | 2026-09-04T12:26:12.8022023Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.006 | 16043 |
| 2026-09-04T12:26:12.8312521Z | 2026-09-04T12:28:30.5913060Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, x86_64-pc-windows-msvc) | 2.296 | 16102 |
| 2026-09-04T12:28:30.5945269Z | 2026-09-04T12:34:58.9376548Z | Building stage2 cargo (stage1 -> stage2, x86_64-pc-windows-msvc) | 6.472 | 16269 |
| 2026-09-04T12:34:58.9396858Z | 2026-09-04T12:38:26.7318263Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-pc-windows-msvc) | 3.463 | 16976 |
| 2026-09-04T12:38:26.7345599Z | 2026-09-04T12:38:27.2428105Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.008 | 17154 |
| 2026-09-04T12:38:29.2019364Z | 2026-09-04T12:38:29.3633769Z | Building bootstrap | 0.003 | 17316 |
| 2026-09-04T12:38:30.3034102Z | 2026-09-04T12:47:12.7057528Z | Building LLVM for x86_64-pc-windows-msvc | 8.707 | 17327 |
| 2026-09-04T12:47:12.9267451Z | 2026-09-04T12:47:32.0945536Z | Building LLD for x86_64-pc-windows-msvc | 0.319 | 24530 |
| 2026-09-04T12:47:32.0953764Z | 2026-09-04T12:47:32.8143112Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.012 | 24769 |
| 2026-09-04T12:47:32.8239635Z | 2026-09-04T12:47:33.2873043Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.008 | 24777 |
| 2026-09-04T12:47:33.2897620Z | 2026-09-04T12:47:33.6721474Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.006 | 24849 |
| 2026-09-04T12:47:33.9727234Z | 2026-09-04T12:47:34.5220283Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.009 | 24918 |
| 2026-09-04T12:47:34.5291376Z | 2026-09-04T12:47:34.9490227Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.007 | 24926 |
| 2026-09-04T12:47:34.9516604Z | 2026-09-04T12:47:35.3261762Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.006 | 24998 |
| 2026-09-04T12:47:35.3818001Z | 2026-09-04T12:54:43.1230173Z | Running benchmarks | 7.129 | 25099 |
| 2026-09-04T12:54:50.4530151Z | 2026-09-04T12:54:50.6717134Z | Building bootstrap | 0.004 | 25158 |
| 2026-09-04T12:54:52.1551245Z | 2026-09-04T13:01:32.6576120Z | Building LLVM for x86_64-pc-windows-msvc | 6.675 | 25170 |
| 2026-09-04T13:01:32.8039467Z | 2026-09-04T13:01:48.7279061Z | Building LLD for x86_64-pc-windows-msvc | 0.265 | 32370 |
| 2026-09-04T13:01:48.7287018Z | 2026-09-04T13:01:49.2548873Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.009 | 32609 |
| 2026-09-04T13:01:49.2617763Z | 2026-09-04T13:01:49.6301805Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.006 | 32617 |
| 2026-09-04T13:01:49.6326100Z | 2026-09-04T13:01:49.9770924Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.006 | 32689 |
| 2026-09-04T13:01:49.9818476Z | 2026-09-04T13:01:50.4877214Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-pc-windows-msvc) | 0.008 | 32742 |
| 2026-09-04T13:01:50.4895250Z | 2026-09-04T13:02:44.2680168Z | Building stage1 unstable-book-gen (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.896 | 32781 |
| 2026-09-04T13:02:46.1595971Z | 2026-09-04T13:03:41.2576119Z | Building stage1 rustbook (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.918 | 33016 |
| 2026-09-04T13:03:47.5837056Z | 2026-09-04T13:03:47.5914075Z | Documenting stage2 book redirect pages (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 33445 |
| 2026-09-04T13:03:47.5914811Z | 2026-09-04T13:06:32.9885310Z | Building stage1 rustdoc-tool-binary (stage0 -> stage1, x86_64-pc-windows-msvc) | 2.757 | 33449 |
| 2026-09-04T13:06:32.9886327Z | 2026-09-04T13:06:35.1899345Z | Documenting stage2 book redirect pages (stage1 -> stage2, x86_64-pc-windows-msvc) (continued) | 0.037 | 33633 |
| 2026-09-04T13:06:35.1906063Z | 2026-09-04T13:06:36.0062028Z | Documenting stage2 standalone (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.014 | 33639 |
| 2026-09-04T13:06:36.0086837Z | 2026-09-04T13:07:44.6918064Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage1 -> stage1, x86_64-pc-windows-msvc) | 1.145 | 33643 |
| 2026-09-04T13:07:44.7039746Z | 2026-09-04T13:09:08.4869681Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-pc-windows-msvc) | 1.396 | 33703 |
| 2026-09-04T13:09:08.4908040Z | 2026-09-04T13:09:37.4987783Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.483 | 34038 |
| 2026-09-04T13:09:37.5009275Z | 2026-09-04T13:09:37.8238041Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.005 | 34094 |
| 2026-09-04T13:09:37.8318348Z | 2026-09-04T13:09:38.2274927Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.007 | 34102 |
| 2026-09-04T13:09:38.2304496Z | 2026-09-04T13:09:38.6064081Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.006 | 34174 |
| 2026-09-04T13:09:38.6108076Z | 2026-09-04T13:10:21.4193461Z | Building stage2 error_index_generator (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.713 | 34228 |
| 2026-09-04T13:10:35.9578451Z | 2026-09-04T13:10:42.0636039Z | Building stage1 lint-docs (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.102 | 34561 |
| 2026-09-04T13:10:42.1026964Z | 2026-09-04T13:11:03.3236050Z | Running stage2 lint-docs (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.354 | 34592 |
| 2026-09-04T13:11:05.9744861Z | 2026-09-04T13:11:06.1836713Z | Documenting stage2 releases (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.003 | 34650 |
| 2026-09-04T13:11:31.0076547Z | 2026-09-04T13:12:01.9059507Z | Building stage1 rust-installer (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.515 | 34655 |
| 2026-09-04T13:13:17.8743092Z | 2026-09-04T13:13:33.3918409Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage1 -> stage1, x86_64-pc-windows-msvc) | 0.259 | 34740 |
| 2026-09-04T13:13:41.2200983Z | 2026-09-04T13:15:47.5838588Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, x86_64-pc-windows-msvc) | 2.106 | 34782 |
| 2026-09-04T13:15:47.5886259Z | 2026-09-04T13:16:39.3591269Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.863 | 34892 |
| 2026-09-04T13:16:39.4243019Z | 2026-09-04T13:18:02.6175853Z | Vendoring sources to "C:\\a\\rust\\rust" | 1.387 | 35083 |
| 2026-09-04T13:18:02.6179721Z | 2026-09-04T13:18:02.6188275Z | generate-copyright | 0.000 | 37258 |
| 2026-09-04T13:18:02.6188777Z | 2026-09-04T13:18:38.3128730Z | Building stage1 generate-copyright (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.595 | 37262 |
| 2026-09-04T13:18:38.3131934Z | 2026-09-04T13:18:42.1612949Z | generate-copyright (continued) | 0.064 | 37407 |
| 2026-09-04T13:21:01.0812892Z | 2026-09-04T13:21:01.9964486Z | Vendoring sources to "C:\\a\\rust\\rust\\build\\tmp\\tarball\\rust-src\\image\\lib/rustlib/src/rust" | 0.015 | 41797 |
| 2026-09-04T13:21:14.0803165Z | 2026-09-04T13:21:15.2304478Z | Building stage2 cargo (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.019 | 41839 |
| 2026-09-04T13:21:25.8649033Z | 2026-09-04T13:26:56.7867787Z | Building stage2 rust-analyzer (stage1 -> stage2, x86_64-pc-windows-msvc) | 5.515 | 42234 |
| 2026-09-04T13:27:07.5973485Z | 2026-09-04T13:28:18.4714213Z | Building stage2 rustfmt (stage1 -> stage2, x86_64-pc-windows-msvc) | 1.181 | 42737 |
| 2026-09-04T13:28:18.4740919Z | 2026-09-04T13:28:18.9210785Z | Building stage2 cargo-fmt (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.007 | 42921 |
| 2026-09-04T13:28:23.8562079Z | 2026-09-04T13:31:19.4110827Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-pc-windows-msvc) | 2.926 | 43035 |
| 2026-09-04T13:31:19.4137199Z | 2026-09-04T13:31:19.8767252Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.008 | 43146 |
| 2026-09-04T13:31:27.3536975Z | 2026-09-04T13:33:05.4464616Z | Building stage2 miri (stage1 -> stage2, x86_64-pc-windows-msvc) | 1.635 | 43257 |
| 2026-09-04T13:33:05.4491739Z | 2026-09-04T13:33:19.3364151Z | Building stage2 cargo-miri (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.231 | 43459 |
| 2026-09-04T13:38:31.7515896Z | 2026-09-04T13:38:56.1014962Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage2 -> stage2, x86_64-pc-windows-msvc) | 0.406 | 43557 |
| 2026-09-04T13:46:46.5985362Z | 2026-09-04T13:47:18.9751803Z | Building bootstrap | 0.540 | 43805 |
| 2026-09-04T13:47:23.4513669Z | 2026-09-04T13:48:00.0909559Z | Building stage1 compiletest (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.611 | 43888 |
| 2026-09-04T13:48:00.1132013Z | 2026-09-04T13:48:17.5768307Z | Testing stage0 with compiletest suite=assembly-llvm mode=assembly (x86_64-pc-windows-msvc) | 0.291 | 43978 |
| 2026-09-04T13:48:17.5875491Z | 2026-09-04T13:48:35.2207667Z | Testing stage0 with compiletest suite=codegen-llvm mode=codegen (x86_64-pc-windows-msvc) | 0.294 | 44758 |
| 2026-09-04T13:48:35.2316107Z | 2026-09-04T13:48:36.2787584Z | Testing stage0 with compiletest suite=codegen-units mode=codegen-units (x86_64-pc-windows-msvc) | 0.017 | 45985 |
| 2026-09-04T13:48:36.2892565Z | 2026-09-04T13:48:36.3668232Z | Building test helpers for x86_64-pc-windows-msvc | 0.001 | 46038 |
| 2026-09-04T13:48:36.3671556Z | 2026-09-04T13:48:50.6602100Z | Testing stage0 with compiletest suite=incremental mode=incremental (x86_64-pc-windows-msvc) | 0.238 | 46041 |
| 2026-09-04T13:48:50.6710072Z | 2026-09-04T13:49:03.1490212Z | Testing stage0 with compiletest suite=mir-opt mode=mir-opt (x86_64-pc-windows-msvc) | 0.208 | 46228 |
| 2026-09-04T13:49:03.1596883Z | 2026-09-04T13:49:04.8114304Z | Testing stage0 with compiletest suite=pretty mode=pretty (x86_64-pc-windows-msvc) | 0.028 | 46645 |
| 2026-09-04T13:49:04.8223414Z | 2026-09-04T13:49:24.5753234Z | Building stage1 run_make_support (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.329 | 46766 |
| 2026-09-04T13:49:24.5760140Z | 2026-09-04T13:49:24.7836532Z | Testing stage0 with compiletest suite=run-make mode=run-make (x86_64-pc-windows-msvc) | 0.003 | 46799 |
| 2026-09-04T13:49:24.7977702Z | 2026-09-04T13:56:44.0411247Z | Testing stage0 with compiletest suite=ui mode=ui (x86_64-pc-windows-msvc) | 7.321 | 46808 |
| 2026-09-04T13:56:44.0568884Z | 2026-09-04T13:56:46.1858338Z | Testing stage0 with compiletest suite=crashes mode=crashes (x86_64-pc-windows-msvc) | 0.035 | 68998 |
| 2026-09-04T13:12:01.9478254Z | 2026-09-04T13:13:17.8724303Z | Dist rust-docs-nightly-x86_64-pc-windows-msvc | 1.265 | 34735 |
| 2026-09-04T13:13:33.4448319Z | 2026-09-04T13:13:41.2113001Z | Dist rust-docs-json-nightly-x86_64-pc-windows-msvc | 0.129 | 34774 |
| 2026-09-04T13:18:42.2203689Z | 2026-09-04T13:19:27.6214073Z | Dist rustc-nightly-x86_64-pc-windows-msvc | 0.757 | 41776 |
| 2026-09-04T13:19:27.6772398Z | 2026-09-04T13:19:33.0800975Z | Dist rustc-codegen-cranelift-nightly-x86_64-pc-windows-msvc | 0.090 | 41780 |
| 2026-09-04T13:19:33.1510465Z | 2026-09-04T13:19:46.5359872Z | Dist rust-std-nightly-x86_64-pc-windows-msvc | 0.223 | 41784 |
| 2026-09-04T13:19:47.7304944Z | 2026-09-04T13:20:59.5870680Z | Dist rustc-dev-nightly-x86_64-pc-windows-msvc | 1.198 | 41788 |
| 2026-09-04T13:20:59.6412302Z | 2026-09-04T13:20:59.6844316Z | Dist rust-analysis-nightly-x86_64-pc-windows-msvc | 0.001 | 41792 |
| 2026-09-04T13:21:02.0464883Z | 2026-09-04T13:21:14.0786681Z | Dist rust-src-nightly | 0.201 | 41833 |
| 2026-09-04T13:21:15.3028081Z | 2026-09-04T13:21:25.8632194Z | Dist cargo-nightly-x86_64-pc-windows-msvc | 0.176 | 42228 |
| 2026-09-04T13:26:56.8516399Z | 2026-09-04T13:27:07.5956222Z | Dist rust-analyzer-nightly-x86_64-pc-windows-msvc | 0.179 | 42731 |
| 2026-09-04T13:28:18.9767884Z | 2026-09-04T13:28:23.8547207Z | Dist rustfmt-nightly-x86_64-pc-windows-msvc | 0.081 | 43029 |
| 2026-09-04T13:31:19.9338033Z | 2026-09-04T13:31:27.3522491Z | Dist clippy-nightly-x86_64-pc-windows-msvc | 0.124 | 43251 |
| 2026-09-04T13:33:19.3957629Z | 2026-09-04T13:33:24.3419494Z | Dist miri-nightly-x86_64-pc-windows-msvc | 0.082 | 43536 |
| 2026-09-04T13:33:24.4014252Z | 2026-09-04T13:34:02.8275524Z | Dist llvm-tools-nightly-x86_64-pc-windows-msvc | 0.640 | 43540 |
| 2026-09-04T13:34:02.8839063Z | 2026-09-04T13:34:04.4410757Z | Dist llvm-bitcode-linker-nightly-x86_64-pc-windows-msvc | 0.026 | 43544 |
| 2026-09-04T13:34:05.9689495Z | 2026-09-04T13:38:31.7469687Z | Dist rust-dev-nightly-x86_64-pc-windows-msvc | 4.430 | 43550 |
| 2026-09-04T13:38:56.1755162Z | 2026-09-04T13:39:03.9183119Z | Dist rust-docs-json-nightly-x86_64-pc-windows-msvc | 0.129 | 43612 |
| 2026-09-04T13:39:03.9701118Z | 2026-09-04T13:43:00.8307782Z | Dist rust-nightly-x86_64-pc-windows-msvc | 3.948 | 43615 |
| 2026-09-04T13:43:53.6615042Z | 2026-09-04T13:46:03.4195981Z | MSI package | 2.163 | 43629 |
| 2026-09-04T13:46:03.4773997Z | 2026-09-04T13:46:22.6792010Z | Dist reproducible-artifacts-nightly-x86_64-pc-windows-msvc | 0.320 | 43634 |
| 2026-09-04T13:46:22.7368292Z | 2026-09-04T13:46:32.1656944Z | Dist bootstrap-nightly-x86_64-pc-windows-msvc | 0.157 | 43638 |

</details>

| opt-dist timer (nested) | Minutes |
|---|---:|
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Build PGO instrumented rustc and LLVM | 49.029 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather rustc profiles | 13.920 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather rustdoc profiles | 2.009 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather clippy profiles | 2.853 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Build PGO optimized rustc | 21.175 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) | 88.987 |
| Stage 2 (LLVM PGO) > Build PGO instrumented LLVM | 9.105 |
| Stage 2 (LLVM PGO) > Gather profiles | 7.209 |
| Stage 2 (LLVM PGO) | 16.383 |
| Stage 5 (final build) | 51.699 |
| Run tests | 11.118 |

## [auto - aarch64-msvc-1: 100999918199](https://github.com/rust-lang/rust/actions/runs/33865610474/job/100999918199)

Run 33865610474; raw SHA256 `0c806d78feaa6559ce6f519b8c6c2fc812ad7a790f3c7bd61c47568431537d41`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 1.324 |
| Build support | 1.175 |
| LLVM/LLD | 12.478 |
| Compiler | 31.529 |
| Tools | 22.624 |
| Libraries | 1.374 |
| Tests | 49.584 |
| Docs | 4.711 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-04T11:09:45.3589133Z | 2026-09-04T11:09:45.3624630Z | Run set +e | 0.000 | 1803 |
| 2026-09-04T11:09:48.0915028Z | 2026-09-04T11:09:48.3394812Z | Clock drift check | 0.004 | 1849 |
| 2026-09-04T11:09:50.2916929Z | 2026-09-04T11:09:50.2937516Z | Configure the build | 0.000 | 1855 |
| 2026-09-04T11:10:00.4056720Z | 2026-09-04T11:11:09.2038793Z | Building bootstrap | 1.147 | 1900 |
| 2026-09-04T11:11:10.7661850Z | 2026-09-04T11:11:10.7750394Z | Building LLVM for aarch64-pc-windows-msvc | 0.000 | 2080 |
| 2026-09-04T11:11:10.7785169Z | 2026-09-04T11:11:10.7795681Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2082 |
| 2026-09-04T11:11:10.7803327Z | 2026-09-04T11:11:10.7804038Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2085 |
| 2026-09-04T11:11:10.7812632Z | 2026-09-04T11:11:10.7835692Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2087 |
| 2026-09-04T11:11:10.7846214Z | 2026-09-04T11:11:10.7849185Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2089 |
| 2026-09-04T11:11:10.7854002Z | 2026-09-04T11:11:10.7856742Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2091 |
| 2026-09-04T11:11:10.7872909Z | 2026-09-04T11:11:10.7878010Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2093 |
| 2026-09-04T11:11:10.7882976Z | 2026-09-04T11:11:10.7887150Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2095 |
| 2026-09-04T11:11:10.7894159Z | 2026-09-04T11:11:10.7894836Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2098 |
| 2026-09-04T11:11:10.7900720Z | 2026-09-04T11:11:10.7903942Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2100 |
| 2026-09-04T11:11:10.7946648Z | 2026-09-04T11:11:10.7949449Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2102 |
| 2026-09-04T11:11:10.7953923Z | 2026-09-04T11:11:10.7956330Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2104 |
| 2026-09-04T11:11:10.7978182Z | 2026-09-04T11:11:10.7980952Z | Building stage2 cargo (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2107 |
| 2026-09-04T11:11:10.7985682Z | 2026-09-04T11:11:10.7988161Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2109 |
| 2026-09-04T11:11:10.8005473Z | 2026-09-04T11:11:10.8007751Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2111 |
| 2026-09-04T11:11:10.8033258Z | 2026-09-04T11:11:10.8035441Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2113 |
| 2026-09-04T11:11:10.8042307Z | 2026-09-04T11:11:10.8045096Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2115 |
| 2026-09-04T11:11:10.8050494Z | 2026-09-04T11:11:10.8053220Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2117 |
| 2026-09-04T11:11:10.8059324Z | 2026-09-04T11:11:10.8061601Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2119 |
| 2026-09-04T11:11:10.8067423Z | 2026-09-04T11:11:10.8070081Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2121 |
| 2026-09-04T11:11:10.8075946Z | 2026-09-04T11:11:10.8078527Z | Building stage2 miri (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2123 |
| 2026-09-04T11:11:10.8085452Z | 2026-09-04T11:11:10.8087963Z | Building stage2 cargo-miri (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2125 |
| 2026-09-04T11:11:10.8349915Z | 2026-09-04T11:11:11.4521724Z | Display CPU and Memory information | 0.010 | 2128 |
| 2026-09-04T11:11:11.7747047Z | 2026-09-04T11:11:11.9559954Z | Building bootstrap | 0.003 | 2236 |
| 2026-09-04T11:11:16.6089930Z | 2026-09-04T11:23:17.2308614Z | Building LLVM for aarch64-pc-windows-msvc | 12.010 | 2348 |
| 2026-09-04T11:23:17.4449551Z | 2026-09-04T11:35:41.6642452Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 12.404 | 9531 |
| 2026-09-04T11:35:41.7102988Z | 2026-09-04T11:37:36.8955641Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.920 | 10322 |
| 2026-09-04T11:37:36.9073428Z | 2026-09-04T11:38:04.9824102Z | Building LLD for aarch64-pc-windows-msvc | 0.468 | 10444 |
| 2026-09-04T11:38:08.3123003Z | 2026-09-04T11:38:09.8676216Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.026 | 10685 |
| 2026-09-04T11:38:09.8821349Z | 2026-09-04T11:39:11.8393300Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.033 | 10694 |
| 2026-09-04T11:39:11.8474287Z | 2026-09-04T11:39:26.1097762Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.238 | 10844 |
| 2026-09-04T11:39:26.1238225Z | 2026-09-04T11:40:48.5818561Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 1.374 | 10925 |
| 2026-09-04T11:40:48.5839404Z | 2026-09-04T11:59:56.1195717Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 19.126 | 10981 |
| 2026-09-04T11:59:56.1253764Z | 2026-09-04T12:02:53.9433629Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-pc-windows-msvc) | 2.964 | 11585 |
| 2026-09-04T12:02:53.9466177Z | 2026-09-04T12:02:55.3206519Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.023 | 11679 |
| 2026-09-04T12:02:55.3304223Z | 2026-09-04T12:05:03.5149279Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 2.136 | 11688 |
| 2026-09-04T12:05:03.5181239Z | 2026-09-04T12:05:33.3302413Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.497 | 11817 |
| 2026-09-04T12:05:33.3861317Z | 2026-09-04T12:06:10.6490758Z | Building stage1 compiletest (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.621 | 11904 |
| 2026-09-04T12:06:10.6818298Z | 2026-09-04T12:06:10.8007922Z | Building test helpers for aarch64-pc-windows-msvc | 0.002 | 12088 |
| 2026-09-04T12:06:10.8297747Z | 2026-09-04T12:26:31.8288290Z | Testing stage2 with compiletest suite=ui mode=ui (aarch64-pc-windows-msvc) | 20.350 | 12092 |
| 2026-09-04T12:26:31.8667227Z | 2026-09-04T12:26:38.9564780Z | Testing stage2 with compiletest suite=crashes mode=crashes (aarch64-pc-windows-msvc) | 0.118 | 34270 |
| 2026-09-04T12:26:38.9831597Z | 2026-09-04T12:26:44.3921489Z | Building stage1 coverage-dump (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.090 | 34485 |
| 2026-09-04T12:26:44.3939481Z | 2026-09-04T12:26:51.3422471Z | Testing stage2 with compiletest suite=coverage mode=coverage-map (aarch64-pc-windows-msvc) | 0.116 | 34531 |
| 2026-09-04T12:26:51.3716511Z | 2026-09-04T12:26:51.5921991Z | Testing stage2 with compiletest suite=coverage mode=coverage-run (aarch64-pc-windows-msvc) | 0.004 | 34647 |
| 2026-09-04T12:26:51.6161710Z | 2026-09-04T12:27:24.4034741Z | Testing stage2 with compiletest suite=mir-opt mode=mir-opt (aarch64-pc-windows-msvc) | 0.546 | 34768 |
| 2026-09-04T12:27:24.4316353Z | 2026-09-04T12:28:21.4548174Z | Testing stage2 with compiletest suite=codegen-llvm mode=codegen (aarch64-pc-windows-msvc) | 0.950 | 35189 |
| 2026-09-04T12:28:21.4834994Z | 2026-09-04T12:28:24.2879879Z | Testing stage2 with compiletest suite=codegen-units mode=codegen-units (aarch64-pc-windows-msvc) | 0.047 | 36412 |
| 2026-09-04T12:28:24.3159129Z | 2026-09-04T12:29:16.3641148Z | Testing stage2 with compiletest suite=assembly-llvm mode=assembly (aarch64-pc-windows-msvc) | 0.867 | 36469 |
| 2026-09-04T12:29:16.3920145Z | 2026-09-04T12:29:54.7130869Z | Testing stage2 with compiletest suite=incremental mode=incremental (aarch64-pc-windows-msvc) | 0.639 | 37253 |
| 2026-09-04T12:29:57.0180859Z | 2026-09-04T12:30:33.4257097Z | Testing stage2 with compiletest suite=debuginfo mode=debuginfo (aarch64-pc-windows-msvc) | 0.607 | 37446 |
| 2026-09-04T12:30:33.6622523Z | 2026-09-04T12:31:11.1002040Z | Testing stage2 with compiletest suite=ui-fulldeps mode=ui (aarch64-pc-windows-msvc) | 0.624 | 37981 |
| 2026-09-04T12:31:11.1338948Z | 2026-09-04T12:34:05.3215451Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 2.903 | 38072 |
| 2026-09-04T12:34:05.3251572Z | 2026-09-04T12:36:20.3984465Z | Testing stage2 with compiletest suite=rustdoc-html mode=rustdoc-html (aarch64-pc-windows-msvc) | 2.251 | 38277 |
| 2026-09-04T12:36:20.4316935Z | 2026-09-04T12:36:20.6466203Z | Testing stage2 with compiletest suite=coverage-run-rustdoc mode=coverage-run (aarch64-pc-windows-msvc) | 0.004 | 39091 |
| 2026-09-04T12:36:20.6751135Z | 2026-09-04T12:36:25.7449708Z | Testing stage2 with compiletest suite=pretty mode=pretty (aarch64-pc-windows-msvc) | 0.084 | 39105 |
| 2026-09-04T12:36:25.7906753Z | 2026-09-04T12:47:23.7928972Z | Testing stage2 {alloc, alloctests, compiler_builtins, core, coretests, panic_abort, panic_unwind, proc_macro, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} (aarch64-pc-windows-msvc) | 10.967 | 39236 |
| 2026-09-04T12:47:23.7990173Z | 2026-09-04T12:48:24.4904509Z | Testing stage1 tidy (aarch64-pc-windows-msvc) | 1.012 | 55283 |
| 2026-09-04T12:48:24.4971370Z | 2026-09-04T12:49:57.3437131Z | Building stage2 error_index_generator (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.547 | 55592 |
| 2026-09-04T12:49:57.3455721Z | 2026-09-04T12:49:57.3923457Z | Testing stage2 error-index (aarch64-pc-windows-msvc) | 0.001 | 55875 |
| 2026-09-04T12:50:47.5759371Z | 2026-09-04T12:51:21.5080601Z | Testing stage1 stdarch-verify (aarch64-pc-windows-msvc) | 0.566 | 57005 |
| 2026-09-04T12:51:21.5449528Z | 2026-09-04T12:54:31.3765468Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage2 -> stage2, aarch64-pc-windows-msvc) | 3.164 | 57090 |
| 2026-09-04T12:54:31.3801240Z | 2026-09-04T12:55:17.9202228Z | Testing stage2 rustdoc-js-std (aarch64-pc-windows-msvc) | 0.776 | 57144 |
| 2026-09-04T12:55:17.9915236Z | 2026-09-04T12:55:43.5307500Z | Testing stage2 with compiletest suite=rustdoc-js mode=rustdoc-js (aarch64-pc-windows-msvc) | 0.426 | 57216 |
| 2026-09-04T12:55:43.5835394Z | 2026-09-04T12:56:20.9191603Z | Testing stage2 with compiletest suite=rustdoc-ui mode=ui (aarch64-pc-windows-msvc) | 0.622 | 57307 |
| 2026-09-04T12:56:20.9659756Z | 2026-09-04T12:56:45.6459534Z | Building stage1 jsondocck (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.411 | 57766 |
| 2026-09-04T12:56:45.6483669Z | 2026-09-04T12:56:59.4389916Z | Building stage1 jsondoclint (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.230 | 57900 |
| 2026-09-04T12:56:59.4401721Z | 2026-09-04T12:57:17.9802113Z | Testing stage2 with compiletest suite=rustdoc-json mode=rustdoc-json (aarch64-pc-windows-msvc) | 0.309 | 57954 |
| 2026-09-04T12:57:18.0365052Z | 2026-09-04T12:57:31.7249257Z | Building stage1 run_make_support (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.228 | 58161 |
| 2026-09-04T12:57:31.7288014Z | 2026-09-04T13:01:30.1793758Z | Testing stage2 with compiletest suite=run-make mode=run-make (aarch64-pc-windows-msvc) | 3.974 | 58244 |
| 2026-09-04T13:01:30.2513436Z | 2026-09-04T13:10:48.5064017Z | Building stage2 cargo (stage1 -> stage2, aarch64-pc-windows-msvc) | 9.304 | 58778 |
| 2026-09-04T13:10:48.5095266Z | 2026-09-04T13:14:32.0201523Z | Testing stage2 with compiletest suite=run-make-cargo mode=run-make (aarch64-pc-windows-msvc) | 3.725 | 59714 |
| 2026-09-04T13:14:32.4105205Z | 2026-09-04T13:14:32.5543961Z | sccache stats | 0.002 | 59744 |
| 2026-09-04T13:14:32.5613650Z | 2026-09-04T13:14:32.9564815Z | Clock drift check | 0.007 | 59781 |

</details>

## [auto - dist-aarch64-linux: 101163495648](https://github.com/rust-lang/rust/actions/runs/33916006473/job/101163495648)

Run 33916006473; raw SHA256 `40bc8ee9d68d18ff1dc9d095c7a599de494027a5a3cc99a7cbc70baed5f57bb1`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 2.228 |
| Build support | 1.965 |
| LLVM/LLD | 26.829 |
| Compiler | 13.219 |
| Tools | 23.009 |
| Libraries | 0.438 |
| Tests | 10.887 |
| Docs | 5.941 |
| Packaging | 4.233 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-04T20:30:07.5439700Z | 2026-09-04T20:30:07.5478137Z | Run set +e | 0.000 | 1742 |
| 2026-09-04T20:30:07.7607258Z | 2026-09-04T20:30:07.7681985Z | Image checksum input | 0.000 | 1785 |
| 2026-09-04T20:30:07.7702157Z | 2026-09-04T20:30:47.2257031Z | Building docker image for dist-aarch64-linux | 0.658 | 2176 |
| 2026-09-04T20:30:48.0194586Z | 2026-09-04T20:30:48.1675742Z | Clock drift check | 0.002 | 2285 |
| 2026-09-04T20:30:48.4668292Z | 2026-09-04T20:30:48.4685706Z | Configure the build | 0.000 | 2291 |
| 2026-09-04T20:30:57.5326224Z | 2026-09-04T20:31:08.9900305Z | Building bootstrap | 0.191 | 2346 |
| 2026-09-04T20:31:09.1894863Z | 2026-09-04T20:31:09.1895264Z | Building LLVM for aarch64-unknown-linux-gnu | 0.000 | 2479 |
| 2026-09-04T20:31:09.2128912Z | 2026-09-04T20:31:09.2130011Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2481 |
| 2026-09-04T20:31:09.2131157Z | 2026-09-04T20:31:09.2131591Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2484 |
| 2026-09-04T20:31:09.2133176Z | 2026-09-04T20:31:09.2133846Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2486 |
| 2026-09-04T20:31:09.2136674Z | 2026-09-04T20:31:09.2137264Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2488 |
| 2026-09-04T20:31:09.2137619Z | 2026-09-04T20:31:09.2138022Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2490 |
| 2026-09-04T20:31:09.2139971Z | 2026-09-04T20:31:09.2140365Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2492 |
| 2026-09-04T20:31:09.2141806Z | 2026-09-04T20:31:09.2142213Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2494 |
| 2026-09-04T20:31:09.2143649Z | 2026-09-04T20:31:09.2144064Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2497 |
| 2026-09-04T20:31:09.2144988Z | 2026-09-04T20:31:09.2154494Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2499 |
| 2026-09-04T20:31:09.2154848Z | 2026-09-04T20:31:09.2155260Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2501 |
| 2026-09-04T20:31:09.2155608Z | 2026-09-04T20:31:09.2156006Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2503 |
| 2026-09-04T20:31:09.2156559Z | 2026-09-04T20:31:09.2156930Z | Building stage2 cargo (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2506 |
| 2026-09-04T20:31:09.2157516Z | 2026-09-04T20:31:09.2157902Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2508 |
| 2026-09-04T20:31:09.2158292Z | 2026-09-04T20:31:09.2158819Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2510 |
| 2026-09-04T20:31:09.2159436Z | 2026-09-04T20:31:09.2159838Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2512 |
| 2026-09-04T20:31:09.2160170Z | 2026-09-04T20:31:09.2160552Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2514 |
| 2026-09-04T20:31:09.2160887Z | 2026-09-04T20:31:09.2161264Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2516 |
| 2026-09-04T20:31:09.2161586Z | 2026-09-04T20:31:09.2162080Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2518 |
| 2026-09-04T20:31:09.2163011Z | 2026-09-04T20:31:09.2163480Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2520 |
| 2026-09-04T20:31:09.2251972Z | 2026-09-04T20:31:09.2287583Z | Display CPU and Memory information | 0.000 | 2523 |
| 2026-09-04T20:31:09.2817741Z | 2026-09-04T20:31:09.3286050Z | Building bootstrap | 0.001 | 2654 |
| 2026-09-04T20:31:09.5486593Z | 2026-09-04T20:31:31.2091183Z | Building stage1 opt-dist (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.361 | 2665 |
| 2026-09-04T20:31:31.2181280Z | 2026-09-04T20:31:31.2200662Z | Environment values | 0.000 | 2898 |
| 2026-09-04T20:31:31.2200922Z | 2026-09-04T20:31:31.2260030Z | Printing bootstrap.toml | 0.000 | 2951 |
| 2026-09-04T20:31:31.2260282Z | 2026-09-04T20:32:05.0427740Z | Building rustc-perf | 0.564 | 3186 |
| 2026-09-04T20:32:05.0971108Z | 2026-09-04T20:32:05.1452641Z | Building bootstrap | 0.001 | 3766 |
| 2026-09-04T20:32:05.3961552Z | 2026-09-04T20:34:25.2952224Z | Building LLVM for aarch64-unknown-linux-gnu | 2.332 | 3775 |
| 2026-09-04T20:34:25.3074448Z | 2026-09-04T20:39:16.4195792Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-unknown-linux-gnu) | 4.852 | 11348 |
| 2026-09-04T20:39:16.4303685Z | 2026-09-04T20:40:51.5270775Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-unknown-linux-gnu) | 1.585 | 12050 |
| 2026-09-04T20:40:51.5274457Z | 2026-09-04T20:40:55.8359489Z | Building LLD for aarch64-unknown-linux-gnu | 0.072 | 12167 |
| 2026-09-04T20:40:55.8362974Z | 2026-09-04T20:40:56.1502153Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.005 | 12439 |
| 2026-09-04T20:40:56.1508424Z | 2026-09-04T20:41:17.5035757Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.356 | 12448 |
| 2026-09-04T20:41:17.5041423Z | 2026-09-04T20:41:21.3055116Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.063 | 12589 |
| 2026-09-04T20:41:21.4623843Z | 2026-09-04T20:41:31.4009606Z | Building sanitizers for aarch64-unknown-linux-gnu | 0.166 | 12662 |
| 2026-09-04T20:41:31.4016155Z | 2026-09-04T20:41:57.5649106Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-unknown-linux-gnu) | 0.436 | 13421 |
| 2026-09-04T20:41:57.5722601Z | 2026-09-04T20:46:06.3174289Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-unknown-linux-gnu) | 4.146 | 13499 |
| 2026-09-04T20:46:06.3278818Z | 2026-09-04T20:47:59.0773110Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-unknown-linux-gnu) | 1.879 | 14104 |
| 2026-09-04T20:47:59.0777932Z | 2026-09-04T20:47:59.4399352Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.006 | 14198 |
| 2026-09-04T20:47:59.4404954Z | 2026-09-04T20:48:24.1691111Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.412 | 14207 |
| 2026-09-04T20:48:24.1697148Z | 2026-09-04T20:48:28.6107894Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.074 | 14334 |
| 2026-09-04T20:48:28.6128380Z | 2026-09-04T20:50:13.3988473Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, aarch64-unknown-linux-gnu) | 1.746 | 14408 |
| 2026-09-04T20:50:13.3995817Z | 2026-09-04T20:55:04.9984409Z | Building stage2 cargo (stage1 -> stage2, aarch64-unknown-linux-gnu) | 4.860 | 14610 |
| 2026-09-04T20:55:05.0086454Z | 2026-09-04T20:59:43.6784627Z | Running benchmarks | 4.644 | 15499 |
| 2026-09-04T21:00:24.2714957Z | 2026-09-04T21:00:54.6989973Z | Running benchmarks | 0.507 | 15619 |
| 2026-09-04T21:01:06.9275185Z | 2026-09-04T21:01:07.0543002Z | Building bootstrap | 0.002 | 15674 |
| 2026-09-04T21:01:07.6187994Z | 2026-09-04T21:01:08.3068593Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.011 | 15698 |
| 2026-09-04T21:01:08.3594663Z | 2026-09-04T21:01:08.4695675Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.002 | 16024 |
| 2026-09-04T21:01:08.4701271Z | 2026-09-04T21:01:08.5773573Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.002 | 16081 |
| 2026-09-04T21:01:08.5780486Z | 2026-09-04T21:01:08.7827102Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.003 | 16089 |
| 2026-09-04T21:01:08.7832999Z | 2026-09-04T21:01:08.9219474Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.002 | 16161 |
| 2026-09-04T21:01:09.1328651Z | 2026-09-04T21:01:09.2381509Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-unknown-linux-gnu) | 0.002 | 16213 |
| 2026-09-04T21:01:09.2454075Z | 2026-09-04T21:05:21.8499790Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-unknown-linux-gnu) | 4.210 | 16254 |
| 2026-09-04T21:05:21.9001238Z | 2026-09-04T21:05:36.1154476Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.237 | 16829 |
| 2026-09-04T21:05:36.1159140Z | 2026-09-04T21:05:36.2291926Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 16885 |
| 2026-09-04T21:05:36.2297507Z | 2026-09-04T21:05:36.4147152Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.003 | 16893 |
| 2026-09-04T21:05:36.4152981Z | 2026-09-04T21:05:36.5584834Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 16965 |
| 2026-09-04T21:05:36.5604082Z | 2026-09-04T21:06:59.2018127Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, aarch64-unknown-linux-gnu) | 1.377 | 17020 |
| 2026-09-04T21:06:59.2025702Z | 2026-09-04T21:10:56.5618510Z | Building stage2 cargo (stage1 -> stage2, aarch64-unknown-linux-gnu) | 3.956 | 17187 |
| 2026-09-04T21:10:57.0825317Z | 2026-09-04T21:10:57.1415957Z | Building bootstrap | 0.001 | 17946 |
| 2026-09-04T21:10:57.4015052Z | 2026-09-04T21:17:31.9162718Z | Building LLVM for aarch64-unknown-linux-gnu | 6.575 | 17955 |
| 2026-09-04T21:17:31.9281605Z | 2026-09-04T21:17:41.6896803Z | Building LLD for aarch64-unknown-linux-gnu | 0.163 | 25543 |
| 2026-09-04T21:17:41.6900111Z | 2026-09-04T21:17:41.8060295Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.002 | 25819 |
| 2026-09-04T21:17:41.8066138Z | 2026-09-04T21:17:41.9289849Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.002 | 25827 |
| 2026-09-04T21:17:41.9295570Z | 2026-09-04T21:17:42.0469054Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.002 | 25899 |
| 2026-09-04T21:17:42.2111746Z | 2026-09-04T21:17:42.3177188Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 25966 |
| 2026-09-04T21:17:42.3182846Z | 2026-09-04T21:17:42.4413580Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 25974 |
| 2026-09-04T21:17:42.4419213Z | 2026-09-04T21:17:42.5565100Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 26046 |
| 2026-09-04T21:17:42.5681840Z | 2026-09-04T21:20:34.3225944Z | Running benchmarks | 2.863 | 26100 |
| 2026-09-04T21:21:13.2817216Z | 2026-09-04T21:21:13.3912524Z | Building bootstrap | 0.002 | 26202 |
| 2026-09-04T21:21:13.7484226Z | 2026-09-04T21:38:45.2382620Z | Building LLVM for aarch64-unknown-linux-gnu | 17.525 | 26212 |
| 2026-09-04T21:38:45.2919604Z | 2026-09-04T21:38:55.0529310Z | Building LLD for aarch64-unknown-linux-gnu | 0.163 | 33795 |
| 2026-09-04T21:38:55.0532952Z | 2026-09-04T21:38:55.1759502Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.002 | 34071 |
| 2026-09-04T21:38:55.1765105Z | 2026-09-04T21:38:55.3348664Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.003 | 34079 |
| 2026-09-04T21:38:55.3355011Z | 2026-09-04T21:38:55.4643002Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.002 | 34151 |
| 2026-09-04T21:38:55.6388892Z | 2026-09-04T21:39:01.3981343Z | Building stage1 unstable-book-gen (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.096 | 34211 |
| 2026-09-04T21:39:02.1560248Z | 2026-09-04T21:39:25.6002611Z | Building stage1 rustbook (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.391 | 34443 |
| 2026-09-04T21:39:29.3624051Z | 2026-09-04T21:39:29.3639287Z | Documenting stage2 book redirect pages (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 34869 |
| 2026-09-04T21:39:29.3640148Z | 2026-09-04T21:40:40.1222477Z | Building stage1 rustdoc_tool_binary (stage0 -> stage1, aarch64-unknown-linux-gnu) | 1.179 | 34873 |
| 2026-09-04T21:40:40.1222970Z | 2026-09-04T21:40:40.6639295Z | Documenting stage2 book redirect pages (stage1 -> stage2, aarch64-unknown-linux-gnu) (continued) | 0.009 | 35056 |
| 2026-09-04T21:40:40.6641715Z | 2026-09-04T21:40:40.8731748Z | Documenting stage2 standalone (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.003 | 35062 |
| 2026-09-04T21:40:40.8736358Z | 2026-09-04T21:40:56.3437513Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage1 -> stage1, aarch64-unknown-linux-gnu) | 0.258 | 35066 |
| 2026-09-04T21:40:56.3462102Z | 2026-09-04T21:42:18.8363714Z | Documenting stage2 compiler{rustc-main, rustc_abi, rustc_arena, rustc_ast, rustc_ast_ir, rustc_ast_lowering, rustc_ast_passes, rustc_ast_pretty, rustc_attr_ir, rustc_attr_parsing, rustc_baked_icu_data, rustc_borrowck, rustc_builtin_macros, rustc_codegen_llvm, rustc_codegen_ssa, rustc_const_eval, rustc_crate_store, rustc_data_structures, rustc_driver, rustc_driver_impl, rustc_error_codes, rustc_error_messages, rustc_errors, rustc_expand, rustc_feature, rustc_fs_util, rustc_graphviz, rustc_hashes, rustc_hir, rustc_hir_analysis, rustc_hir_id, rustc_hir_pretty, rustc_hir_typeck, rustc_incremental, rustc_index, rustc_index_macros, rustc_infer, rustc_interface, rustc_lexer, rustc_lint, rustc_lint_defs, rustc_llvm, rustc_log, rustc_macros, rustc_metadata, rustc_middle, rustc_mir_build, rustc_mir_dataflow, rustc_mir_transform, rustc_monomorphize, rustc_next_trait_solver, rustc_parse, rustc_parse_format, rustc_passes, rustc_pattern_analysis, rustc_privacy, rustc_proc_macro, rustc_public, rustc_public_bridge, rustc_query_impl, rustc_resolve, rustc_sanitizers, rustc_serialize, rustc_session, rustc_span, rustc_symbol_mangling, rustc_target, rustc_thread_pool, rustc_trait_selection, rustc_traits, rustc_transmute, rustc_ty_utils, rustc_ty_walk, rustc_type_ir, rustc_type_ir_macros, rustc_windows_rc} (stage1 -> stage2, aarch64-unknown-linux-gnu) | 1.375 | 35132 |
| 2026-09-04T21:42:18.8849649Z | 2026-09-04T21:42:18.9925221Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 35823 |
| 2026-09-04T21:42:18.9931048Z | 2026-09-04T21:42:19.1480374Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.003 | 35831 |
| 2026-09-04T21:42:19.1485972Z | 2026-09-04T21:42:19.2762730Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 35903 |
| 2026-09-04T21:42:19.2778220Z | 2026-09-04T21:42:33.6481556Z | Documenting stage2 rustdoc (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.240 | 35950 |
| 2026-09-04T21:42:33.6491954Z | 2026-09-04T21:42:52.5977921Z | Documenting stage2 rustfmt (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.316 | 36135 |
| 2026-09-04T21:42:52.5984611Z | 2026-09-04T21:43:05.7626493Z | Building stage2 error_index_generator (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.219 | 36326 |
| 2026-09-04T21:43:15.7758142Z | 2026-09-04T21:43:17.2914346Z | Building stage1 lint-docs (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.025 | 36663 |
| 2026-09-04T21:43:17.2967173Z | 2026-09-04T21:43:30.8338337Z | Running stage2 lint-docs (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.226 | 36697 |
| 2026-09-04T21:43:31.3449799Z | 2026-09-04T21:44:52.0558742Z | Documenting stage2 cargo (stage1 -> stage2, aarch64-unknown-linux-gnu) | 1.345 | 36710 |
| 2026-09-04T21:44:52.4540498Z | 2026-09-04T21:45:00.0109417Z | Documenting stage2 clippy (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.126 | 37535 |
| 2026-09-04T21:45:00.1268068Z | 2026-09-04T21:45:18.1299842Z | Documenting stage2 miri (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.300 | 37579 |
| 2026-09-04T21:45:18.3972447Z | 2026-09-04T21:45:28.9275206Z | Documenting stage2 tidy (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.176 | 37771 |
| 2026-09-04T21:45:28.9280132Z | 2026-09-04T21:45:47.4238020Z | Documenting stage2 bootstrap (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.308 | 37986 |
| 2026-09-04T21:45:47.4240987Z | 2026-09-04T21:45:47.4843863Z | Documenting stage2 releases (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.001 | 38128 |
| 2026-09-04T21:45:47.4847322Z | 2026-09-04T21:45:53.8342645Z | Documenting stage2 runmakesupport (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.106 | 38132 |
| 2026-09-04T21:45:53.8347578Z | 2026-09-04T21:45:56.6476099Z | Documenting stage2 buildhelper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.047 | 38224 |
| 2026-09-04T21:45:56.6480900Z | 2026-09-04T21:46:02.3087215Z | Documenting stage2 compiletest (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.094 | 38231 |
| 2026-09-04T21:46:02.9769769Z | 2026-09-04T21:46:10.9775117Z | Building stage1 rust-installer (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.133 | 38371 |
| 2026-09-04T21:47:03.5284263Z | 2026-09-04T21:47:10.1104099Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage1 -> stage1, aarch64-unknown-linux-gnu) | 0.110 | 38457 |
| 2026-09-04T21:47:14.2396179Z | 2026-09-04T21:47:14.4287103Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.003 | 38506 |
| 2026-09-04T21:47:14.4294324Z | 2026-09-04T21:47:32.2202609Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.297 | 38615 |
| 2026-09-04T21:47:32.2317020Z | 2026-09-04T21:47:43.5227028Z | Vendoring sources to "/checkout" | 0.188 | 38802 |
| 2026-09-04T21:47:43.5228529Z | 2026-09-04T21:47:43.5231354Z | generate-copyright | 0.000 | 40959 |
| 2026-09-04T21:47:43.5231716Z | 2026-09-04T21:47:49.6380893Z | Building stage1 generate-copyright (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.102 | 40963 |
| 2026-09-04T21:47:49.6381180Z | 2026-09-04T21:47:51.1470205Z | generate-copyright (continued) | 0.025 | 41108 |
| 2026-09-04T21:48:47.3028072Z | 2026-09-04T21:48:47.3940466Z | Vendoring sources to "/checkout/obj/build/tmp/tarball/rust-src/image/lib/rustlib/src/rust" | 0.002 | 45479 |
| 2026-09-04T21:48:53.4807332Z | 2026-09-04T21:48:53.8963126Z | Building stage2 cargo (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.007 | 45520 |
| 2026-09-04T21:49:01.5536899Z | 2026-09-04T21:51:04.6653870Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-unknown-linux-gnu) | 2.052 | 45919 |
| 2026-09-04T21:51:11.8409763Z | 2026-09-04T21:51:37.9212989Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.435 | 46413 |
| 2026-09-04T21:51:37.9220979Z | 2026-09-04T21:51:38.0632491Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 46590 |
| 2026-09-04T21:51:39.5559395Z | 2026-09-04T21:53:04.5352026Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-unknown-linux-gnu) | 1.416 | 46702 |
| 2026-09-04T21:53:04.5358808Z | 2026-09-04T21:53:04.6811255Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 46863 |
| 2026-09-04T21:53:37.5481044Z | 2026-09-04T21:53:47.8107318Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage2 -> stage2, aarch64-unknown-linux-gnu) | 0.171 | 46986 |
| 2026-09-04T21:55:09.3529033Z | 2026-09-04T21:55:19.3949582Z | Building stage2 build-manifest (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.167 | 47066 |
| 2026-09-04T21:55:30.3026585Z | 2026-09-04T21:55:39.8488375Z | Building bootstrap | 0.159 | 47370 |
| 2026-09-04T21:55:40.2115092Z | 2026-09-04T21:55:49.9848680Z | Building stage1 compiletest (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.163 | 47437 |
| 2026-09-04T21:55:49.9960155Z | 2026-09-04T21:55:54.2631360Z | Testing stage0 with compiletest suite=assembly-llvm mode=assembly (aarch64-unknown-linux-gnu) | 0.071 | 47517 |
| 2026-09-04T21:55:54.2700124Z | 2026-09-04T21:55:58.6068747Z | Testing stage0 with compiletest suite=codegen-llvm mode=codegen (aarch64-unknown-linux-gnu) | 0.072 | 48262 |
| 2026-09-04T21:55:58.6138477Z | 2026-09-04T21:55:58.8769312Z | Testing stage0 with compiletest suite=codegen-units mode=codegen-units (aarch64-unknown-linux-gnu) | 0.004 | 49429 |
| 2026-09-04T21:55:58.8838061Z | 2026-09-04T21:55:58.9417089Z | Building test helpers for aarch64-unknown-linux-gnu | 0.001 | 49482 |
| 2026-09-04T21:55:58.9418764Z | 2026-09-04T21:56:04.0586239Z | Testing stage0 with compiletest suite=incremental mode=incremental (aarch64-unknown-linux-gnu) | 0.085 | 49484 |
| 2026-09-04T21:56:04.0656236Z | 2026-09-04T21:56:05.7696413Z | Testing stage0 with compiletest suite=mir-opt mode=mir-opt (aarch64-unknown-linux-gnu) | 0.028 | 49671 |
| 2026-09-04T21:56:05.7775046Z | 2026-09-04T21:56:06.1569201Z | Testing stage0 with compiletest suite=pretty mode=pretty (aarch64-unknown-linux-gnu) | 0.006 | 50086 |
| 2026-09-04T21:56:06.1572870Z | 2026-09-04T21:56:11.5535467Z | Building stage1 run_make_support (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.090 | 50207 |
| 2026-09-04T21:56:11.5609709Z | 2026-09-04T21:56:11.6081239Z | Testing stage0 with compiletest suite=run-make mode=run-make (aarch64-unknown-linux-gnu) | 0.001 | 50238 |
| 2026-09-04T21:56:11.6149042Z | 2026-09-04T21:58:33.4866762Z | Testing stage0 with compiletest suite=ui mode=ui (aarch64-unknown-linux-gnu) | 2.365 | 50247 |
| 2026-09-04T21:58:33.4949807Z | 2026-09-04T21:58:34.0029642Z | Testing stage0 with compiletest suite=crashes mode=crashes (aarch64-unknown-linux-gnu) | 0.008 | 72283 |
| 2026-09-04T21:58:34.0103680Z | 2026-09-04T21:58:47.9142416Z | Testing stage0 with compiletest suite=rustdoc-html mode=rustdoc-html (aarch64-unknown-linux-gnu) | 0.232 | 72469 |
| 2026-09-04T21:58:47.9245837Z | 2026-09-04T21:58:47.9264700Z | sccache stats | 0.000 | 73342 |
| 2026-09-04T21:58:47.9264945Z | 2026-09-04T21:58:48.0941527Z | Clock drift check | 0.003 | 73385 |
| 2026-09-04T21:46:10.9829969Z | 2026-09-04T21:46:30.1656079Z | Dist rust-docs-beta-aarch64-unknown-linux-gnu | 0.320 | 38448 |
| 2026-09-04T21:46:30.8197030Z | 2026-09-04T21:47:03.5280034Z | Dist rustc-docs-beta-aarch64-unknown-linux-gnu | 0.545 | 38452 |
| 2026-09-04T21:47:10.1163741Z | 2026-09-04T21:47:14.2388897Z | Dist rust-docs-json-beta-aarch64-unknown-linux-gnu | 0.069 | 38498 |
| 2026-09-04T21:47:51.1552005Z | 2026-09-04T21:48:09.0694459Z | Dist rustc-beta-aarch64-unknown-linux-gnu | 0.299 | 45460 |
| 2026-09-04T21:48:09.0767242Z | 2026-09-04T21:48:16.8242040Z | Dist rust-std-beta-aarch64-unknown-linux-gnu | 0.129 | 45466 |
| 2026-09-04T21:48:16.9364529Z | 2026-09-04T21:48:47.0512573Z | Dist rustc-dev-beta-aarch64-unknown-linux-gnu | 0.502 | 45470 |
| 2026-09-04T21:48:47.0575355Z | 2026-09-04T21:48:47.0786361Z | Dist rust-analysis-beta-aarch64-unknown-linux-gnu | 0.000 | 45474 |
| 2026-09-04T21:48:47.4001049Z | 2026-09-04T21:48:53.4802954Z | Dist rust-src-beta | 0.101 | 45514 |
| 2026-09-04T21:48:53.9049233Z | 2026-09-04T21:49:01.5529726Z | Dist cargo-beta-aarch64-unknown-linux-gnu | 0.127 | 45913 |
| 2026-09-04T21:51:04.6722024Z | 2026-09-04T21:51:11.8402895Z | Dist rust-analyzer-beta-aarch64-unknown-linux-gnu | 0.119 | 46407 |
| 2026-09-04T21:51:38.0700788Z | 2026-09-04T21:51:39.5552854Z | Dist rustfmt-beta-aarch64-unknown-linux-gnu | 0.025 | 46696 |
| 2026-09-04T21:53:04.6879402Z | 2026-09-04T21:53:08.3885590Z | Dist clippy-beta-aarch64-unknown-linux-gnu | 0.062 | 46963 |
| 2026-09-04T21:53:08.3959128Z | 2026-09-04T21:53:18.0764592Z | Dist llvm-tools-beta-aarch64-unknown-linux-gnu | 0.161 | 46969 |
| 2026-09-04T21:53:18.0830009Z | 2026-09-04T21:53:18.4993917Z | Dist llvm-bitcode-linker-beta-aarch64-unknown-linux-gnu | 0.007 | 46973 |
| 2026-09-04T21:53:18.7943190Z | 2026-09-04T21:53:37.5473266Z | Dist rust-dev-beta-aarch64-unknown-linux-gnu | 0.313 | 46979 |
| 2026-09-04T21:53:47.8218265Z | 2026-09-04T21:53:51.9399223Z | Dist rust-docs-json-beta-aarch64-unknown-linux-gnu | 0.069 | 47053 |
| 2026-09-04T21:53:51.9461493Z | 2026-09-04T21:54:57.8072548Z | Dist rust-beta-aarch64-unknown-linux-gnu | 1.098 | 47056 |
| 2026-09-04T21:54:57.9191539Z | 2026-09-04T21:55:09.3525116Z | Dist reproducible-artifacts-beta-aarch64-unknown-linux-gnu | 0.191 | 47060 |
| 2026-09-04T21:55:19.4013112Z | 2026-09-04T21:55:19.7936992Z | Dist build-manifest-beta-aarch64-unknown-linux-gnu | 0.007 | 47187 |
| 2026-09-04T21:55:19.8000982Z | 2026-09-04T21:55:25.2548689Z | Dist bootstrap-beta-aarch64-unknown-linux-gnu | 0.091 | 47191 |

</details>

| opt-dist timer (nested) | Minutes |
|---|---:|
| Stage 1 (Rustc + rustdoc PGO) > Build PGO instrumented rustc and LLVM | 22.999 |
| Stage 1 (Rustc + rustdoc PGO) > Gather rustc profiles | 5.321 |
| Stage 1 (Rustc + rustdoc PGO) > Gather rustdoc profiles | 0.709 |
| Stage 1 (Rustc + rustdoc PGO) > Build PGO optimized rustc | 9.829 |
| Stage 1 (Rustc + rustdoc PGO) | 38.859 |
| Stage 2 (LLVM PGO) > Build PGO instrumented LLVM | 6.759 |
| Stage 2 (LLVM PGO) > Gather profiles | 3.505 |
| Stage 2 (LLVM PGO) | 10.277 |
| Stage 5 (final build) | 34.201 |
| Run tests | 3.377 |

## [auto - dist-x86_64-linux: 101163495919](https://github.com/rust-lang/rust/actions/runs/33916006473/job/101163495919)

Run 33916006473; raw SHA256 `1c3730b04722549d57bbfc21f580d6e7f158256aae4d67d289be9fed694022e6`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 20.424 |
| Build support | 11.528 |
| LLVM/LLD | 22.212 |
| Compiler | 18.598 |
| Tools | 38.775 |
| Libraries | 0.839 |
| Tests | 31.813 |
| Docs | 9.239 |
| Packaging | 16.707 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-04T20:31:06.0933152Z | 2026-09-04T20:31:06.0967488Z | Run set +e | 0.000 | 1925 |
| 2026-09-04T20:31:06.2066626Z | 2026-09-04T20:31:06.2239949Z | Image checksum input | 0.000 | 1972 |
| 2026-09-04T20:31:06.2242379Z | 2026-09-04T20:31:41.6938861Z | Building docker image for dist-x86_64-linux | 0.591 | 2407 |
| 2026-09-04T20:32:52.4761878Z | 2026-09-04T20:32:52.4973706Z | Clock drift check | 0.000 | 2527 |
| 2026-09-04T20:32:52.8878836Z | 2026-09-04T20:32:52.8910560Z | Configure the build | 0.000 | 2533 |
| 2026-09-04T20:33:07.7072071Z | 2026-09-04T20:33:26.3644300Z | Building bootstrap | 0.311 | 2585 |
| 2026-09-04T20:33:26.6567190Z | 2026-09-04T20:33:26.6567916Z | Building LLVM for x86_64-unknown-linux-gnu | 0.000 | 2718 |
| 2026-09-04T20:33:26.6955813Z | 2026-09-04T20:33:26.6956698Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2720 |
| 2026-09-04T20:33:26.6958374Z | 2026-09-04T20:33:26.6959216Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2723 |
| 2026-09-04T20:33:26.6961293Z | 2026-09-04T20:33:26.6962107Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2725 |
| 2026-09-04T20:33:26.6963926Z | 2026-09-04T20:33:26.6964951Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2727 |
| 2026-09-04T20:33:26.6966526Z | 2026-09-04T20:33:26.6967335Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2729 |
| 2026-09-04T20:33:26.6971652Z | 2026-09-04T20:33:26.6972478Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2731 |
| 2026-09-04T20:33:26.6975031Z | 2026-09-04T20:33:26.6976270Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2733 |
| 2026-09-04T20:33:26.6979152Z | 2026-09-04T20:33:26.6980070Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2736 |
| 2026-09-04T20:33:26.6981316Z | 2026-09-04T20:33:26.6982080Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2738 |
| 2026-09-04T20:33:26.6985106Z | 2026-09-04T20:33:26.6985934Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2740 |
| 2026-09-04T20:33:26.6987835Z | 2026-09-04T20:33:26.6988643Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2742 |
| 2026-09-04T20:33:26.7003502Z | 2026-09-04T20:33:26.7004331Z | Building stage2 cargo (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2745 |
| 2026-09-04T20:33:26.7004964Z | 2026-09-04T20:33:26.7005698Z | Building stage2 rust-analyzer (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2747 |
| 2026-09-04T20:33:26.7006452Z | 2026-09-04T20:33:26.7007315Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2749 |
| 2026-09-04T20:33:26.7008009Z | 2026-09-04T20:33:26.7008824Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2751 |
| 2026-09-04T20:33:26.7009492Z | 2026-09-04T20:33:26.7010265Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2753 |
| 2026-09-04T20:33:26.7010944Z | 2026-09-04T20:33:26.7011712Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2755 |
| 2026-09-04T20:33:26.7013250Z | 2026-09-04T20:33:26.7014179Z | Building stage2 rustfmt (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2757 |
| 2026-09-04T20:33:26.7016176Z | 2026-09-04T20:33:26.7016942Z | Building stage2 cargo-fmt (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2759 |
| 2026-09-04T20:33:26.7276280Z | 2026-09-04T20:33:26.7844209Z | Display CPU and Memory information | 0.001 | 2762 |
| 2026-09-04T20:33:26.8199406Z | 2026-09-04T20:33:26.9024891Z | Building bootstrap | 0.001 | 3785 |
| 2026-09-04T20:33:27.2212311Z | 2026-09-04T20:33:57.3044582Z | Building stage1 opt-dist (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.501 | 3796 |
| 2026-09-04T20:33:57.3547867Z | 2026-09-04T20:33:57.3591074Z | Environment values | 0.000 | 4031 |
| 2026-09-04T20:33:57.3591588Z | 2026-09-04T20:33:57.3692849Z | Printing bootstrap.toml | 0.000 | 4085 |
| 2026-09-04T20:33:57.3693335Z | 2026-09-04T20:34:33.5345004Z | Building rustc-perf | 0.603 | 4294 |
| 2026-09-04T20:34:33.6187766Z | 2026-09-04T20:34:33.6991572Z | Building bootstrap | 0.001 | 4877 |
| 2026-09-04T20:34:34.0456374Z | 2026-09-04T20:36:21.5198249Z | Building LLVM for x86_64-unknown-linux-gnu | 1.791 | 4886 |
| 2026-09-04T20:36:21.5356170Z | 2026-09-04T20:44:30.4944848Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-unknown-linux-gnu) | 8.149 | 12464 |
| 2026-09-04T20:44:30.5072635Z | 2026-09-04T20:47:17.5084356Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-unknown-linux-gnu) | 2.783 | 13167 |
| 2026-09-04T20:47:17.5091340Z | 2026-09-04T20:47:21.9228772Z | Building LLD for x86_64-unknown-linux-gnu | 0.074 | 13284 |
| 2026-09-04T20:47:21.9234580Z | 2026-09-04T20:47:22.4122946Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.008 | 13556 |
| 2026-09-04T20:47:22.4133598Z | 2026-09-04T20:47:54.2341323Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.530 | 13565 |
| 2026-09-04T20:47:54.2352195Z | 2026-09-04T20:48:00.5804708Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.106 | 13706 |
| 2026-09-04T20:48:06.6637974Z | 2026-09-04T20:48:22.7130453Z | Building sanitizers for x86_64-unknown-linux-gnu | 0.267 | 13779 |
| 2026-09-04T20:48:22.7139496Z | 2026-09-04T20:49:12.6922777Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-unknown-linux-gnu) | 0.833 | 14550 |
| 2026-09-04T20:49:12.7002932Z | 2026-09-04T20:54:13.4520744Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-unknown-linux-gnu) | 5.013 | 14628 |
| 2026-09-04T20:54:13.4634864Z | 2026-09-04T20:57:31.9488543Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-unknown-linux-gnu) | 3.308 | 15230 |
| 2026-09-04T20:57:31.9497302Z | 2026-09-04T20:57:32.4816962Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.009 | 15324 |
| 2026-09-04T20:57:32.4827334Z | 2026-09-04T20:58:12.1069365Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.660 | 15333 |
| 2026-09-04T20:58:12.1080123Z | 2026-09-04T20:58:19.9917872Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.131 | 15460 |
| 2026-09-04T20:58:20.0048339Z | 2026-09-04T21:01:10.3737159Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, x86_64-unknown-linux-gnu) | 2.839 | 15534 |
| 2026-09-04T21:01:10.4654745Z | 2026-09-04T21:08:15.1277669Z | Building stage2 cargo (stage1 -> stage2, x86_64-unknown-linux-gnu) | 7.078 | 15734 |
| 2026-09-04T21:08:15.1762525Z | 2026-09-04T21:14:44.8027220Z | Running benchmarks | 6.494 | 16623 |
| 2026-09-04T21:15:17.5745777Z | 2026-09-04T21:15:48.4344088Z | Running benchmarks | 0.514 | 16744 |
| 2026-09-04T21:16:08.7957121Z | 2026-09-04T21:16:09.1095106Z | Building bootstrap | 0.005 | 16798 |
| 2026-09-04T21:16:11.5223584Z | 2026-09-04T21:16:13.4642915Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.032 | 16822 |
| 2026-09-04T21:16:13.5989302Z | 2026-09-04T21:16:13.8535493Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.004 | 17149 |
| 2026-09-04T21:16:13.8545169Z | 2026-09-04T21:16:14.1026648Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.004 | 17206 |
| 2026-09-04T21:16:14.1037667Z | 2026-09-04T21:16:14.5163292Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.007 | 17214 |
| 2026-09-04T21:16:14.5173947Z | 2026-09-04T21:16:14.7728940Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.004 | 17286 |
| 2026-09-04T21:16:15.2154482Z | 2026-09-04T21:16:15.5501843Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-unknown-linux-gnu) | 0.006 | 17338 |
| 2026-09-04T21:16:15.5582701Z | 2026-09-04T21:21:39.8097362Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-unknown-linux-gnu) | 5.404 | 17379 |
| 2026-09-04T21:21:39.9498168Z | 2026-09-04T21:22:07.5082107Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.459 | 17951 |
| 2026-09-04T21:22:07.5094643Z | 2026-09-04T21:22:07.6867112Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.003 | 18007 |
| 2026-09-04T21:22:07.6878105Z | 2026-09-04T21:22:08.0286006Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.006 | 18015 |
| 2026-09-04T21:22:08.0296907Z | 2026-09-04T21:22:08.2571922Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.004 | 18087 |
| 2026-09-04T21:22:08.2691211Z | 2026-09-04T21:24:32.5844022Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, x86_64-unknown-linux-gnu) | 2.405 | 18142 |
| 2026-09-04T21:24:32.6642463Z | 2026-09-04T21:29:41.6659672Z | Building stage2 cargo (stage1 -> stage2, x86_64-unknown-linux-gnu) | 5.150 | 18307 |
| 2026-09-04T21:29:43.1598394Z | 2026-09-04T21:29:43.2515667Z | Building bootstrap | 0.002 | 19066 |
| 2026-09-04T21:29:43.6227093Z | 2026-09-04T21:34:33.3668858Z | Building LLVM for x86_64-unknown-linux-gnu | 4.829 | 19075 |
| 2026-09-04T21:34:33.3838977Z | 2026-09-04T21:34:45.1078622Z | Building LLD for x86_64-unknown-linux-gnu | 0.195 | 26668 |
| 2026-09-04T21:34:45.1084600Z | 2026-09-04T21:34:45.2871465Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.003 | 26944 |
| 2026-09-04T21:34:45.2882413Z | 2026-09-04T21:34:45.4963226Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.003 | 26952 |
| 2026-09-04T21:34:45.4974056Z | 2026-09-04T21:34:45.6921842Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.003 | 27024 |
| 2026-09-04T21:34:45.9048058Z | 2026-09-04T21:34:46.0737874Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.003 | 27091 |
| 2026-09-04T21:34:46.0748564Z | 2026-09-04T21:34:46.2751232Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.003 | 27099 |
| 2026-09-04T21:34:46.2762699Z | 2026-09-04T21:34:46.4632411Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.003 | 27171 |
| 2026-09-04T21:34:46.5267888Z | 2026-09-04T21:38:50.4997178Z | Running benchmarks | 4.066 | 27225 |
| 2026-09-04T21:39:21.9942948Z | 2026-09-04T21:39:22.0868449Z | Building bootstrap | 0.002 | 27328 |
| 2026-09-04T21:39:22.4731068Z | 2026-09-04T21:54:30.1385174Z | Building LLVM for x86_64-unknown-linux-gnu | 15.128 | 27337 |
| 2026-09-04T21:54:30.1548038Z | 2026-09-04T21:54:41.8273220Z | Building LLD for x86_64-unknown-linux-gnu | 0.195 | 34930 |
| 2026-09-04T21:54:41.8279237Z | 2026-09-04T21:54:42.0047290Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.003 | 35206 |
| 2026-09-04T21:54:42.0058063Z | 2026-09-04T21:54:42.2117772Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.003 | 35214 |
| 2026-09-04T21:54:42.2128817Z | 2026-09-04T21:54:42.4083876Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.003 | 35286 |
| 2026-09-04T21:54:42.6215128Z | 2026-09-04T21:54:42.7905721Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.003 | 35353 |
| 2026-09-04T21:54:42.7916636Z | 2026-09-04T21:54:42.9936202Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.003 | 35361 |
| 2026-09-04T21:54:42.9947313Z | 2026-09-04T21:54:43.1828175Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.003 | 35433 |
| 2026-09-04T21:56:02.4828746Z | 2026-09-04T22:01:20.1231016Z | Running benchmarks | 5.294 | 35574 |
| 2026-09-04T22:01:20.1245458Z | 2026-09-04T22:01:41.9594636Z | Merging BOLT profiles | 0.364 | 35618 |
| 2026-09-04T22:02:54.5829692Z | 2026-09-04T22:16:32.4176090Z | Running benchmarks | 13.631 | 35677 |
| 2026-09-04T22:16:32.4226530Z | 2026-09-04T22:20:44.1268907Z | Merging BOLT profiles | 4.195 | 35740 |
| 2026-09-04T22:24:05.1241422Z | 2026-09-04T22:24:05.9494533Z | Building bootstrap | 0.014 | 35898 |
| 2026-09-04T22:24:09.3859307Z | 2026-09-04T22:24:10.5680418Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.020 | 35931 |
| 2026-09-04T22:24:10.5690957Z | 2026-09-04T22:24:11.0025411Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.007 | 35939 |
| 2026-09-04T22:24:11.0036424Z | 2026-09-04T22:24:11.2746642Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.005 | 36011 |
| 2026-09-04T22:24:11.7799763Z | 2026-09-04T22:24:19.2399087Z | Building stage1 unstable-book-gen (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.124 | 36071 |
| 2026-09-04T22:24:21.9621210Z | 2026-09-04T22:24:58.5944792Z | Building stage1 rustbook (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.611 | 36303 |
| 2026-09-04T22:25:03.3791937Z | 2026-09-04T22:25:03.3818244Z | Documenting stage2 book redirect pages (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 36729 |
| 2026-09-04T22:25:03.3818963Z | 2026-09-04T22:27:02.9145267Z | Building stage1 rustdoc_tool_binary (stage0 -> stage1, x86_64-unknown-linux-gnu) | 1.992 | 36733 |
| 2026-09-04T22:27:02.9146114Z | 2026-09-04T22:27:03.9224356Z | Documenting stage2 book redirect pages (stage1 -> stage2, x86_64-unknown-linux-gnu) (continued) | 0.017 | 36914 |
| 2026-09-04T22:27:03.9228613Z | 2026-09-04T22:27:04.2664492Z | Documenting stage2 standalone (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.006 | 36920 |
| 2026-09-04T22:27:04.2671404Z | 2026-09-04T22:27:37.1345712Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage1 -> stage1, x86_64-unknown-linux-gnu) | 0.548 | 36924 |
| 2026-09-04T22:27:37.1382418Z | 2026-09-04T22:30:09.1857015Z | Documenting stage2 compiler{rustc-main, rustc_abi, rustc_arena, rustc_ast, rustc_ast_ir, rustc_ast_lowering, rustc_ast_passes, rustc_ast_pretty, rustc_attr_ir, rustc_attr_parsing, rustc_baked_icu_data, rustc_borrowck, rustc_builtin_macros, rustc_codegen_llvm, rustc_codegen_ssa, rustc_const_eval, rustc_crate_store, rustc_data_structures, rustc_driver, rustc_driver_impl, rustc_error_codes, rustc_error_messages, rustc_errors, rustc_expand, rustc_feature, rustc_fs_util, rustc_graphviz, rustc_hashes, rustc_hir, rustc_hir_analysis, rustc_hir_id, rustc_hir_pretty, rustc_hir_typeck, rustc_incremental, rustc_index, rustc_index_macros, rustc_infer, rustc_interface, rustc_lexer, rustc_lint, rustc_lint_defs, rustc_llvm, rustc_log, rustc_macros, rustc_metadata, rustc_middle, rustc_mir_build, rustc_mir_dataflow, rustc_mir_transform, rustc_monomorphize, rustc_next_trait_solver, rustc_parse, rustc_parse_format, rustc_passes, rustc_pattern_analysis, rustc_privacy, rustc_proc_macro, rustc_public, rustc_public_bridge, rustc_query_impl, rustc_resolve, rustc_sanitizers, rustc_serialize, rustc_session, rustc_span, rustc_symbol_mangling, rustc_target, rustc_thread_pool, rustc_trait_selection, rustc_traits, rustc_transmute, rustc_ty_utils, rustc_ty_walk, rustc_type_ir, rustc_type_ir_macros, rustc_windows_rc} (stage1 -> stage2, x86_64-unknown-linux-gnu) | 2.534 | 36990 |
| 2026-09-04T22:30:09.4718129Z | 2026-09-04T22:30:09.6657524Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.003 | 37678 |
| 2026-09-04T22:30:09.6668141Z | 2026-09-04T22:30:10.0545152Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.006 | 37686 |
| 2026-09-04T22:30:10.0556054Z | 2026-09-04T22:30:10.3054035Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.004 | 37758 |
| 2026-09-04T22:30:10.3072028Z | 2026-09-04T22:30:41.0662752Z | Documenting stage2 rustdoc (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.513 | 37805 |
| 2026-09-04T22:30:41.0674620Z | 2026-09-04T22:31:16.9684717Z | Documenting stage2 rustfmt (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.598 | 37988 |
| 2026-09-04T22:31:16.9696574Z | 2026-09-04T22:31:39.4817800Z | Building stage2 error_index_generator (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.375 | 38179 |
| 2026-09-04T22:32:06.0463929Z | 2026-09-04T22:32:07.6297122Z | Building stage1 lint-docs (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.026 | 38516 |
| 2026-09-04T22:32:07.6364956Z | 2026-09-04T22:32:26.4532163Z | Running stage2 lint-docs (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.314 | 38550 |
| 2026-09-04T22:32:27.3241409Z | 2026-09-04T22:33:28.9641206Z | Documenting stage2 cargo (stage1 -> stage2, x86_64-unknown-linux-gnu) | 1.027 | 38563 |
| 2026-09-04T22:33:29.6238143Z | 2026-09-04T22:33:44.1475820Z | Documenting stage2 clippy (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.242 | 39388 |
| 2026-09-04T22:33:44.3439008Z | 2026-09-04T22:34:13.4640095Z | Documenting stage2 miri (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.485 | 39432 |
| 2026-09-04T22:34:13.9553695Z | 2026-09-04T22:34:34.2166188Z | Documenting stage2 tidy (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.338 | 39628 |
| 2026-09-04T22:34:34.2174353Z | 2026-09-04T22:35:01.7918091Z | Documenting stage2 bootstrap (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.460 | 39843 |
| 2026-09-04T22:35:01.7923016Z | 2026-09-04T22:35:01.9129959Z | Documenting stage2 releases (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.002 | 39985 |
| 2026-09-04T22:35:01.9134262Z | 2026-09-04T22:35:14.7830290Z | Documenting stage2 runmakesupport (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.214 | 39989 |
| 2026-09-04T22:35:14.7835111Z | 2026-09-04T22:35:20.3633691Z | Documenting stage2 buildhelper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.093 | 40081 |
| 2026-09-04T22:35:20.3641872Z | 2026-09-04T22:35:31.0475651Z | Documenting stage2 compiletest (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.178 | 40088 |
| 2026-09-04T22:35:31.9316830Z | 2026-09-04T22:35:41.9985757Z | Building stage1 rust-installer (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.168 | 40228 |
| 2026-09-04T22:37:04.0255122Z | 2026-09-04T22:37:16.6481028Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage1 -> stage1, x86_64-unknown-linux-gnu) | 0.210 | 40314 |
| 2026-09-04T22:37:23.1811298Z | 2026-09-04T22:39:15.2716761Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, x86_64-unknown-linux-gnu) | 1.868 | 40363 |
| 2026-09-04T22:39:15.3542829Z | 2026-09-04T22:39:46.1957533Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.514 | 40472 |
| 2026-09-04T22:39:46.2122913Z | 2026-09-04T22:40:10.5603999Z | Vendoring sources to "/checkout" | 0.406 | 40659 |
| 2026-09-04T22:40:10.5606662Z | 2026-09-04T22:40:10.5612099Z | generate-copyright | 0.000 | 42815 |
| 2026-09-04T22:40:10.5612801Z | 2026-09-04T22:40:18.3038180Z | Building stage1 generate-copyright (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.129 | 42819 |
| 2026-09-04T22:40:18.3038723Z | 2026-09-04T22:40:20.8546839Z | generate-copyright (continued) | 0.043 | 42964 |
| 2026-09-04T22:42:04.8205295Z | 2026-09-04T22:42:05.0464008Z | Vendoring sources to "/checkout/obj/build/tmp/tarball/rust-src/image/lib/rustlib/src/rust" | 0.004 | 47335 |
| 2026-09-04T22:42:14.7545922Z | 2026-09-04T22:42:16.0265855Z | Building stage2 cargo (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.021 | 47376 |
| 2026-09-04T22:42:27.7514099Z | 2026-09-04T22:46:09.0245865Z | Building stage2 rust-analyzer (stage1 -> stage2, x86_64-unknown-linux-gnu) | 3.688 | 47775 |
| 2026-09-04T22:46:20.5191795Z | 2026-09-04T22:47:06.8278729Z | Building stage2 rustfmt (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.772 | 48269 |
| 2026-09-04T22:47:06.8292333Z | 2026-09-04T22:47:07.0715660Z | Building stage2 cargo-fmt (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.004 | 48446 |
| 2026-09-04T22:47:09.7005782Z | 2026-09-04T22:49:43.2044441Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-unknown-linux-gnu) | 2.558 | 48558 |
| 2026-09-04T22:49:43.2063930Z | 2026-09-04T22:49:43.4556969Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.004 | 48719 |
| 2026-09-04T22:51:03.9263819Z | 2026-09-04T22:51:23.3230076Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage2 -> stage2, x86_64-unknown-linux-gnu) | 0.323 | 48842 |
| 2026-09-04T22:53:45.2346485Z | 2026-09-04T22:54:11.0764361Z | Vendoring sources to "/checkout/obj/build/tmp/tarball/rustc/src/image" | 0.431 | 48917 |
| 2026-09-04T22:58:06.3471017Z | 2026-09-04T22:58:29.8456612Z | Vendoring sources to "/checkout/obj/build/tmp/tarball/rustc/src-gpl/image" | 0.392 | 51033 |
| 2026-09-04T23:03:51.3746688Z | 2026-09-04T23:04:06.9585963Z | Building stage2 build-manifest (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.260 | 52980 |
| 2026-09-04T23:04:28.6002390Z | 2026-09-04T23:04:45.0683867Z | Building bootstrap | 0.274 | 53294 |
| 2026-09-04T23:04:45.5694213Z | 2026-09-04T23:04:59.9280610Z | Building stage1 compiletest (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.239 | 53361 |
| 2026-09-04T23:04:59.9438227Z | 2026-09-04T23:05:03.2340627Z | Testing stage0 with compiletest suite=assembly-llvm mode=assembly (x86_64-unknown-linux-gnu) | 0.055 | 53441 |
| 2026-09-04T23:05:03.2432249Z | 2026-09-04T23:05:06.4090624Z | Testing stage0 with compiletest suite=codegen-llvm mode=codegen (x86_64-unknown-linux-gnu) | 0.053 | 54186 |
| 2026-09-04T23:05:06.4183959Z | 2026-09-04T23:05:06.6995297Z | Testing stage0 with compiletest suite=codegen-units mode=codegen-units (x86_64-unknown-linux-gnu) | 0.005 | 55353 |
| 2026-09-04T23:05:06.7085445Z | 2026-09-04T23:05:06.7686501Z | Building test helpers for x86_64-unknown-linux-gnu | 0.001 | 55406 |
| 2026-09-04T23:05:06.7687359Z | 2026-09-04T23:05:13.4935461Z | Testing stage0 with compiletest suite=incremental mode=incremental (x86_64-unknown-linux-gnu) | 0.112 | 55408 |
| 2026-09-04T23:05:13.5027348Z | 2026-09-04T23:05:15.1170499Z | Testing stage0 with compiletest suite=mir-opt mode=mir-opt (x86_64-unknown-linux-gnu) | 0.027 | 55595 |
| 2026-09-04T23:05:15.1263056Z | 2026-09-04T23:05:15.5975216Z | Testing stage0 with compiletest suite=pretty mode=pretty (x86_64-unknown-linux-gnu) | 0.008 | 56010 |
| 2026-09-04T23:05:15.5979822Z | 2026-09-04T23:05:24.4401312Z | Building stage1 run_make_support (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.147 | 56131 |
| 2026-09-04T23:05:24.4497563Z | 2026-09-04T23:05:25.0076976Z | Testing stage0 with compiletest suite=run-make mode=run-make (x86_64-unknown-linux-gnu) | 0.009 | 56162 |
| 2026-09-04T23:05:25.0173656Z | 2026-09-04T23:06:45.5924252Z | Testing stage0 with compiletest suite=ui mode=ui (x86_64-unknown-linux-gnu) | 1.343 | 56171 |
| 2026-09-04T23:06:45.6022488Z | 2026-09-04T23:06:46.0242849Z | Testing stage0 with compiletest suite=crashes mode=crashes (x86_64-unknown-linux-gnu) | 0.007 | 78207 |
| 2026-09-04T23:06:46.0341423Z | 2026-09-04T23:06:57.7667613Z | Testing stage0 with compiletest suite=rustdoc-html mode=rustdoc-html (x86_64-unknown-linux-gnu) | 0.196 | 78393 |
| 2026-09-04T23:06:57.8633721Z | 2026-09-04T23:07:14.9589080Z | Building bootstrap | 0.285 | 79277 |
| 2026-09-04T23:07:15.4906790Z | 2026-09-04T23:10:35.5404417Z | Building GCC for x86_64-unknown-linux-gnu -> x86_64-unknown-linux-gnu | 3.334 | 79285 |
| 2026-09-04T23:10:35.5450768Z | 2026-09-04T23:10:55.0349315Z | Building stage1 rust-installer (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.325 | 80153 |
| 2026-09-04T23:11:08.3077630Z | 2026-09-04T23:11:08.3130824Z | sccache stats | 0.000 | 80219 |
| 2026-09-04T23:11:08.3131312Z | 2026-09-04T23:11:08.3457644Z | Clock drift check | 0.001 | 80271 |
| 2026-09-04T22:35:42.0056410Z | 2026-09-04T22:36:12.3558940Z | Dist rust-docs-beta-x86_64-unknown-linux-gnu | 0.506 | 40305 |
| 2026-09-04T22:36:13.2069325Z | 2026-09-04T22:37:04.0246265Z | Dist rustc-docs-beta-x86_64-unknown-linux-gnu | 0.847 | 40309 |
| 2026-09-04T22:37:16.6557352Z | 2026-09-04T22:37:23.1799505Z | Dist rust-docs-json-beta-x86_64-unknown-linux-gnu | 0.109 | 40355 |
| 2026-09-04T22:40:20.8627776Z | 2026-09-04T22:40:56.9454114Z | Dist rustc-beta-x86_64-unknown-linux-gnu | 0.601 | 47316 |
| 2026-09-04T22:40:56.9546840Z | 2026-09-04T22:41:10.1281171Z | Dist rust-std-beta-x86_64-unknown-linux-gnu | 0.220 | 47322 |
| 2026-09-04T22:41:10.2042338Z | 2026-09-04T22:42:04.6924932Z | Dist rustc-dev-beta-x86_64-unknown-linux-gnu | 0.908 | 47326 |
| 2026-09-04T22:42:04.7007184Z | 2026-09-04T22:42:04.7348426Z | Dist rust-analysis-beta-x86_64-unknown-linux-gnu | 0.001 | 47330 |
| 2026-09-04T22:42:05.0543565Z | 2026-09-04T22:42:14.7538160Z | Dist rust-src-beta | 0.162 | 47370 |
| 2026-09-04T22:42:16.0361339Z | 2026-09-04T22:42:27.7501305Z | Dist cargo-beta-x86_64-unknown-linux-gnu | 0.195 | 47769 |
| 2026-09-04T22:46:09.0331862Z | 2026-09-04T22:46:20.5179480Z | Dist rust-analyzer-beta-x86_64-unknown-linux-gnu | 0.191 | 48263 |
| 2026-09-04T22:47:07.0795855Z | 2026-09-04T22:47:09.6992601Z | Dist rustfmt-beta-x86_64-unknown-linux-gnu | 0.044 | 48552 |
| 2026-09-04T22:49:43.4636806Z | 2026-09-04T22:49:49.7450126Z | Dist clippy-beta-x86_64-unknown-linux-gnu | 0.105 | 48819 |
| 2026-09-04T22:49:49.7550413Z | 2026-09-04T22:50:12.5757113Z | Dist llvm-tools-beta-x86_64-unknown-linux-gnu | 0.380 | 48825 |
| 2026-09-04T22:50:12.5836961Z | 2026-09-04T22:50:13.2709031Z | Dist llvm-bitcode-linker-beta-x86_64-unknown-linux-gnu | 0.011 | 48829 |
| 2026-09-04T22:50:13.3619991Z | 2026-09-04T22:51:03.9251792Z | Dist rust-dev-beta-x86_64-unknown-linux-gnu | 0.843 | 48835 |
| 2026-09-04T22:51:23.3427168Z | 2026-09-04T22:51:29.9459556Z | Dist rust-docs-json-beta-x86_64-unknown-linux-gnu | 0.110 | 48909 |
| 2026-09-04T22:51:29.9537286Z | 2026-09-04T22:53:34.4582813Z | Dist rust-beta-x86_64-unknown-linux-gnu | 2.075 | 48912 |
| 2026-09-04T22:54:12.1764340Z | 2026-09-04T22:57:53.1379416Z | Dist rustc-beta-src | 3.683 | 51028 |
| 2026-09-04T22:58:31.3827924Z | 2026-09-04T23:03:19.4562052Z | Dist rustc-beta-src-gpl | 4.801 | 52970 |
| 2026-09-04T23:03:19.7318673Z | 2026-09-04T23:03:51.3739089Z | Dist reproducible-artifacts-beta-x86_64-unknown-linux-gnu | 0.527 | 52974 |
| 2026-09-04T23:04:06.9664903Z | 2026-09-04T23:04:07.6537972Z | Dist build-manifest-beta-x86_64-unknown-linux-gnu | 0.011 | 53101 |
| 2026-09-04T23:04:07.6629757Z | 2026-09-04T23:04:17.0803816Z | Dist bootstrap-beta-x86_64-unknown-linux-gnu | 0.157 | 53105 |
| 2026-09-04T23:10:55.0438869Z | 2026-09-04T23:11:08.2551857Z | Dist gcc-dev-beta-x86_64-unknown-linux-gnu | 0.220 | 80213 |

</details>

| opt-dist timer (nested) | Minutes |
|---|---:|
| Stage 1 (Rustc + rustdoc PGO) > Build PGO instrumented rustc and LLVM | 33.694 |
| Stage 1 (Rustc + rustdoc PGO) > Gather rustc profiles | 7.040 |
| Stage 1 (Rustc + rustdoc PGO) > Gather rustdoc profiles | 0.852 |
| Stage 1 (Rustc + rustdoc PGO) > Build PGO optimized rustc | 13.551 |
| Stage 1 (Rustc + rustdoc PGO) | 55.136 |
| Stage 2 (LLVM PGO) > Build PGO instrumented LLVM | 5.058 |
| Stage 2 (LLVM PGO) > Gather profiles | 4.571 |
| Stage 2 (LLVM PGO) | 9.670 |
| Stage 3 (BOLT) > Build PGO optimized LLVM | 15.356 |
| Stage 3 (BOLT) > Instrument & gather profiles > Gather profiles | 5.713 |
| Stage 3 (BOLT) > Instrument & gather profiles | 7.041 |
| Stage 3 (BOLT) > Instrument & gather profiles > Gather profiles | 17.928 |
| Stage 3 (BOLT) > Instrument & gather profiles | 19.085 |
| Stage 3 (BOLT) > Optimize LLVM and rustc with BOLT | 3.236 |
| Stage 3 (BOLT) | 44.717 |
| Stage 5 (final build) | 40.203 |
| Run tests | 2.677 |

## [auto - aarch64-msvc-1: 101163499138](https://github.com/rust-lang/rust/actions/runs/33916006473/job/101163499138)

Run 33916006473; raw SHA256 `39fa41fd258f9113529f6f9c1463b78b434ba52cccaed75fc9810627e9a2f6ba`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 1.355 |
| Build support | 1.193 |
| LLVM/LLD | 12.731 |
| Compiler | 32.222 |
| Tools | 23.453 |
| Libraries | 1.269 |
| Tests | 48.779 |
| Docs | 4.463 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-04T20:39:04.0481108Z | 2026-09-04T20:39:04.0519208Z | Run set +e | 0.000 | 2007 |
| 2026-09-04T20:39:06.9757597Z | 2026-09-04T20:39:07.2832934Z | Clock drift check | 0.005 | 2053 |
| 2026-09-04T20:39:09.0901876Z | 2026-09-04T20:39:09.0924372Z | Configure the build | 0.000 | 2059 |
| 2026-09-04T20:39:18.4965113Z | 2026-09-04T20:40:29.0561855Z | Building bootstrap | 1.176 | 2104 |
| 2026-09-04T20:40:30.5683614Z | 2026-09-04T20:40:30.5765500Z | Building LLVM for aarch64-pc-windows-msvc | 0.000 | 2284 |
| 2026-09-04T20:40:31.1214869Z | 2026-09-04T20:40:31.1225381Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2286 |
| 2026-09-04T20:40:31.1234631Z | 2026-09-04T20:40:31.1235302Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2289 |
| 2026-09-04T20:40:31.1243512Z | 2026-09-04T20:40:31.1264616Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2291 |
| 2026-09-04T20:40:31.1275138Z | 2026-09-04T20:40:31.1277838Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2293 |
| 2026-09-04T20:40:31.1282492Z | 2026-09-04T20:40:31.1284948Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2295 |
| 2026-09-04T20:40:31.1298759Z | 2026-09-04T20:40:31.1304005Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2297 |
| 2026-09-04T20:40:31.1309724Z | 2026-09-04T20:40:31.1312920Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2299 |
| 2026-09-04T20:40:31.1321110Z | 2026-09-04T20:40:31.1321778Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2302 |
| 2026-09-04T20:40:31.1327627Z | 2026-09-04T20:40:31.1330868Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2304 |
| 2026-09-04T20:40:31.1340790Z | 2026-09-04T20:40:31.1343305Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2306 |
| 2026-09-04T20:40:31.1347735Z | 2026-09-04T20:40:31.1350130Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2308 |
| 2026-09-04T20:40:31.1370235Z | 2026-09-04T20:40:31.1372678Z | Building stage2 cargo (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2311 |
| 2026-09-04T20:40:31.1377477Z | 2026-09-04T20:40:31.1380429Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2313 |
| 2026-09-04T20:40:31.1385504Z | 2026-09-04T20:40:31.1387900Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2315 |
| 2026-09-04T20:40:31.1395218Z | 2026-09-04T20:40:31.1398001Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2317 |
| 2026-09-04T20:40:31.1404803Z | 2026-09-04T20:40:31.1407190Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2319 |
| 2026-09-04T20:40:31.1413416Z | 2026-09-04T20:40:31.1415914Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2321 |
| 2026-09-04T20:40:31.1422207Z | 2026-09-04T20:40:31.1424705Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2323 |
| 2026-09-04T20:40:31.1430480Z | 2026-09-04T20:40:31.1432957Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2325 |
| 2026-09-04T20:40:31.1703759Z | 2026-09-04T20:40:31.4077982Z | Display CPU and Memory information | 0.004 | 2328 |
| 2026-09-04T20:40:31.7112112Z | 2026-09-04T20:40:31.9024316Z | Building bootstrap | 0.003 | 2436 |
| 2026-09-04T20:40:36.2804344Z | 2026-09-04T20:52:51.4579407Z | Building LLVM for aarch64-pc-windows-msvc | 12.253 | 2546 |
| 2026-09-04T20:52:51.5636377Z | 2026-09-04T21:06:02.4258555Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 13.181 | 9729 |
| 2026-09-04T21:06:02.4495630Z | 2026-09-04T21:08:12.8526297Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-pc-windows-msvc) | 2.173 | 10529 |
| 2026-09-04T21:08:12.8649440Z | 2026-09-04T21:08:41.5673474Z | Building LLD for aarch64-pc-windows-msvc | 0.478 | 10649 |
| 2026-09-04T21:08:44.5848791Z | 2026-09-04T21:08:46.2413940Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.028 | 10890 |
| 2026-09-04T21:08:46.2589635Z | 2026-09-04T21:09:55.1067114Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.147 | 10899 |
| 2026-09-04T21:09:55.1136353Z | 2026-09-04T21:10:10.9389064Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.264 | 11051 |
| 2026-09-04T21:10:10.9551502Z | 2026-09-04T21:11:27.1232959Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 1.269 | 11132 |
| 2026-09-04T21:11:27.1250456Z | 2026-09-04T21:30:29.6000501Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 19.041 | 11189 |
| 2026-09-04T21:30:29.6061289Z | 2026-09-04T21:33:30.5840887Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-pc-windows-msvc) | 3.016 | 11799 |
| 2026-09-04T21:33:30.5878325Z | 2026-09-04T21:33:32.0046916Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.024 | 11893 |
| 2026-09-04T21:33:32.0155698Z | 2026-09-04T21:35:39.1396216Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 2.119 | 11902 |
| 2026-09-04T21:35:39.1425014Z | 2026-09-04T21:36:08.3060377Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.486 | 12031 |
| 2026-09-04T21:36:08.3566556Z | 2026-09-04T21:36:47.3812558Z | Building stage1 compiletest (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.650 | 12118 |
| 2026-09-04T21:36:47.4179150Z | 2026-09-04T21:36:47.5403706Z | Building test helpers for aarch64-pc-windows-msvc | 0.002 | 12305 |
| 2026-09-04T21:36:47.5700804Z | 2026-09-04T21:57:36.9188324Z | Testing stage2 with compiletest suite=ui mode=ui (aarch64-pc-windows-msvc) | 20.822 | 12309 |
| 2026-09-04T21:57:36.9646860Z | 2026-09-04T21:57:43.0819239Z | Testing stage2 with compiletest suite=crashes mode=crashes (aarch64-pc-windows-msvc) | 0.102 | 34333 |
| 2026-09-04T21:57:43.1156742Z | 2026-09-04T21:57:49.9918455Z | Building stage1 coverage-dump (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.115 | 34525 |
| 2026-09-04T21:57:49.9947844Z | 2026-09-04T21:57:57.0858437Z | Testing stage2 with compiletest suite=coverage mode=coverage-map (aarch64-pc-windows-msvc) | 0.118 | 34569 |
| 2026-09-04T21:57:57.1147579Z | 2026-09-04T21:57:57.3468376Z | Testing stage2 with compiletest suite=coverage mode=coverage-run (aarch64-pc-windows-msvc) | 0.004 | 34685 |
| 2026-09-04T21:57:57.3703230Z | 2026-09-04T21:58:32.2738729Z | Testing stage2 with compiletest suite=mir-opt mode=mir-opt (aarch64-pc-windows-msvc) | 0.582 | 34806 |
| 2026-09-04T21:58:32.3052240Z | 2026-09-04T21:59:30.0184570Z | Testing stage2 with compiletest suite=codegen-llvm mode=codegen (aarch64-pc-windows-msvc) | 0.962 | 35225 |
| 2026-09-04T21:59:30.0492036Z | 2026-09-04T21:59:33.1778691Z | Testing stage2 with compiletest suite=codegen-units mode=codegen-units (aarch64-pc-windows-msvc) | 0.052 | 36393 |
| 2026-09-04T21:59:33.2086622Z | 2026-09-04T22:00:26.6628723Z | Testing stage2 with compiletest suite=assembly-llvm mode=assembly (aarch64-pc-windows-msvc) | 0.891 | 36450 |
| 2026-09-04T22:00:26.7021623Z | 2026-09-04T22:01:07.6006968Z | Testing stage2 with compiletest suite=incremental mode=incremental (aarch64-pc-windows-msvc) | 0.682 | 37199 |
| 2026-09-04T22:01:09.9097927Z | 2026-09-04T22:01:57.3511404Z | Testing stage2 with compiletest suite=debuginfo mode=debuginfo (aarch64-pc-windows-msvc) | 0.791 | 37392 |
| 2026-09-04T22:01:57.5768793Z | 2026-09-04T22:02:38.1931455Z | Testing stage2 with compiletest suite=ui-fulldeps mode=ui (aarch64-pc-windows-msvc) | 0.677 | 37927 |
| 2026-09-04T22:02:38.2281154Z | 2026-09-04T22:05:39.6819757Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 3.024 | 38016 |
| 2026-09-04T22:05:39.6859263Z | 2026-09-04T22:08:07.2500247Z | Testing stage2 with compiletest suite=rustdoc-html mode=rustdoc-html (aarch64-pc-windows-msvc) | 2.459 | 38219 |
| 2026-09-04T22:08:07.2834755Z | 2026-09-04T22:08:07.5076507Z | Testing stage2 with compiletest suite=coverage-run-rustdoc mode=coverage-run (aarch64-pc-windows-msvc) | 0.004 | 39052 |
| 2026-09-04T22:08:07.5382297Z | 2026-09-04T22:08:13.1421898Z | Testing stage2 with compiletest suite=pretty mode=pretty (aarch64-pc-windows-msvc) | 0.093 | 39066 |
| 2026-09-04T22:08:13.2035113Z | 2026-09-04T22:19:28.5127283Z | Testing stage2 {alloc, alloctests, compiler_builtins, core, coretests, panic_abort, panic_unwind, proc_macro, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} (aarch64-pc-windows-msvc) | 11.255 | 39197 |
| 2026-09-04T22:19:28.5200209Z | 2026-09-04T22:20:33.0666140Z | Testing stage1 tidy (aarch64-pc-windows-msvc) | 1.076 | 55049 |
| 2026-09-04T22:20:33.0748878Z | 2026-09-04T22:22:04.5625110Z | Building stage2 error_index_generator (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.525 | 55354 |
| 2026-09-04T22:22:04.5649754Z | 2026-09-04T22:22:04.6134421Z | Testing stage2 error-index (aarch64-pc-windows-msvc) | 0.001 | 55639 |
| 2026-09-04T22:22:56.6082799Z | 2026-09-04T22:23:42.8711246Z | Testing stage1 stdarch-verify (aarch64-pc-windows-msvc) | 0.771 | 56769 |
| 2026-09-04T22:23:44.1613293Z | 2026-09-04T22:26:40.4766402Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage2 -> stage2, aarch64-pc-windows-msvc) | 2.939 | 56854 |
| 2026-09-04T22:26:40.4820505Z | 2026-09-04T22:27:24.2665655Z | Testing stage2 rustdoc-js-std (aarch64-pc-windows-msvc) | 0.730 | 56905 |
| 2026-09-04T22:27:24.3189328Z | 2026-09-04T22:27:50.4927963Z | Testing stage2 with compiletest suite=rustdoc-js mode=rustdoc-js (aarch64-pc-windows-msvc) | 0.436 | 56977 |
| 2026-09-04T22:27:50.5544091Z | 2026-09-04T22:28:26.0702898Z | Testing stage2 with compiletest suite=rustdoc-ui mode=ui (aarch64-pc-windows-msvc) | 0.592 | 57068 |
| 2026-09-04T22:28:26.1196449Z | 2026-09-04T22:28:53.2865432Z | Building stage1 jsondocck (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.453 | 57500 |
| 2026-09-04T22:28:53.2890913Z | 2026-09-04T22:29:08.7395257Z | Building stage1 jsondoclint (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.258 | 57634 |
| 2026-09-04T22:29:08.7404619Z | 2026-09-04T22:29:24.1101649Z | Testing stage2 with compiletest suite=rustdoc-json mode=rustdoc-json (aarch64-pc-windows-msvc) | 0.256 | 57688 |
| 2026-09-04T22:29:24.1179274Z | 2026-09-04T22:29:37.7294396Z | Building stage1 run_make_support (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.227 | 57895 |
| 2026-09-04T22:29:37.7892026Z | 2026-09-04T22:33:44.6813238Z | Testing stage2 with compiletest suite=run-make mode=run-make (aarch64-pc-windows-msvc) | 4.115 | 57981 |
| 2026-09-04T22:33:44.7474475Z | 2026-09-04T22:43:12.9246552Z | Building stage2 cargo (stage1 -> stage2, aarch64-pc-windows-msvc) | 9.470 | 58507 |
| 2026-09-04T22:43:12.9271381Z | 2026-09-04T22:44:31.4189056Z | Testing stage2 with compiletest suite=run-make-cargo mode=run-make (aarch64-pc-windows-msvc) | 1.308 | 59436 |
| 2026-09-04T22:44:31.7168535Z | 2026-09-04T22:44:31.8508961Z | sccache stats | 0.002 | 59464 |

</details>

## [auto - dist-aarch64-msvc: 101163499162](https://github.com/rust-lang/rust/actions/runs/33916006473/job/101163499162)

Run 33916006473; raw SHA256 `8cb4713630b8836bdce566a4dcb680ed0652102c6418c0dc444b10edf6d8cba1`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 6.884 |
| Build support | 6.297 |
| LLVM/LLD | 12.114 |
| Compiler | 22.988 |
| Tools | 23.037 |
| Libraries | 1.630 |
| Docs | 11.236 |
| Packaging | 26.382 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-04T20:41:06.0814607Z | 2026-09-04T20:41:06.0855345Z | Run set +e | 0.000 | 2085 |
| 2026-09-04T20:41:09.6940733Z | 2026-09-04T20:41:09.9920154Z | Clock drift check | 0.005 | 2133 |
| 2026-09-04T20:41:12.1055719Z | 2026-09-04T20:41:12.1075605Z | Configure the build | 0.000 | 2139 |
| 2026-09-04T20:41:21.4165454Z | 2026-09-04T20:42:37.6277411Z | Building bootstrap | 1.270 | 2184 |
| 2026-09-04T20:42:39.4016266Z | 2026-09-04T20:42:39.4112910Z | Building LLVM for aarch64-pc-windows-msvc | 0.000 | 2364 |
| 2026-09-04T20:42:39.9527445Z | 2026-09-04T20:42:39.9538705Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2366 |
| 2026-09-04T20:42:39.9551164Z | 2026-09-04T20:42:39.9583130Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2369 |
| 2026-09-04T20:42:39.9596313Z | 2026-09-04T20:42:39.9599495Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2371 |
| 2026-09-04T20:42:39.9605962Z | 2026-09-04T20:42:39.9608550Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2373 |
| 2026-09-04T20:42:39.9627147Z | 2026-09-04T20:42:39.9631477Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2375 |
| 2026-09-04T20:42:39.9637372Z | 2026-09-04T20:42:39.9641826Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2377 |
| 2026-09-04T20:42:39.9649917Z | 2026-09-04T20:42:39.9653262Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2380 |
| 2026-09-04T20:42:39.9664044Z | 2026-09-04T20:42:39.9666744Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2382 |
| 2026-09-04T20:42:39.9671671Z | 2026-09-04T20:42:39.9674373Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2384 |
| 2026-09-04T20:42:39.9732973Z | 2026-09-04T20:42:39.9738525Z | Building stage1 library artifacts (stage1:aarch64-pc-windows-msvc -> stage1:arm64ec-pc-windows-msvc) | 0.000 | 2387 |
| 2026-09-04T20:42:39.9785481Z | 2026-09-04T20:42:39.9788313Z | Building stage2 cargo (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2390 |
| 2026-09-04T20:42:39.9794084Z | 2026-09-04T20:42:39.9796971Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2392 |
| 2026-09-04T20:42:39.9802887Z | 2026-09-04T20:42:39.9805724Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2394 |
| 2026-09-04T20:42:39.9814118Z | 2026-09-04T20:42:39.9816986Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2396 |
| 2026-09-04T20:42:39.9824692Z | 2026-09-04T20:42:39.9827317Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2398 |
| 2026-09-04T20:42:39.9834544Z | 2026-09-04T20:42:39.9837460Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2400 |
| 2026-09-04T20:42:39.9844435Z | 2026-09-04T20:42:39.9847041Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2402 |
| 2026-09-04T20:42:39.9853937Z | 2026-09-04T20:42:39.9856815Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2404 |
| 2026-09-04T20:42:40.0164517Z | 2026-09-04T20:42:40.2951532Z | Display CPU and Memory information | 0.005 | 2407 |
| 2026-09-04T20:42:40.5441979Z | 2026-09-04T20:42:40.7433048Z | Building bootstrap | 0.003 | 2515 |
| 2026-09-04T20:42:43.7029548Z | 2026-09-04T20:54:24.9764170Z | Building LLVM for aarch64-pc-windows-msvc | 11.688 | 2525 |
| 2026-09-04T20:54:25.0909195Z | 2026-09-04T21:05:58.8336114Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 11.562 | 9701 |
| 2026-09-04T21:05:58.8490796Z | 2026-09-04T21:06:24.3920276Z | Building LLD for aarch64-pc-windows-msvc | 0.426 | 10502 |
| 2026-09-04T21:06:24.3953128Z | 2026-09-04T21:06:27.7512570Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.056 | 10741 |
| 2026-09-04T21:06:27.7667983Z | 2026-09-04T21:07:33.6699162Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.098 | 10750 |
| 2026-09-04T21:07:33.6774553Z | 2026-09-04T21:07:48.8355216Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.253 | 10902 |
| 2026-09-04T21:07:48.8569326Z | 2026-09-04T21:08:39.4761473Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.844 | 10982 |
| 2026-09-04T21:08:39.5038436Z | 2026-09-04T21:09:32.3147396Z | Building stage1 unstable-book-gen (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.880 | 11047 |
| 2026-09-04T21:09:33.9164028Z | 2026-09-04T21:10:54.2577324Z | Building stage1 rustbook (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.339 | 11298 |
| 2026-09-04T21:10:58.1836782Z | 2026-09-04T21:11:45.3380640Z | Building stage1 library artifacts (stage1:aarch64-pc-windows-msvc -> stage1:arm64ec-pc-windows-msvc) | 0.786 | 11741 |
| 2026-09-04T21:11:52.5071145Z | 2026-09-04T21:11:52.5254156Z | Documenting stage2 book redirect pages (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 11835 |
| 2026-09-04T21:11:52.5256084Z | 2026-09-04T21:13:39.2531439Z | Building stage1 rustdoc_tool_binary (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.779 | 11839 |
| 2026-09-04T21:13:39.2538516Z | 2026-09-04T21:13:42.6724402Z | Documenting stage2 book redirect pages (stage1 -> stage2, aarch64-pc-windows-msvc) (continued) | 0.057 | 12040 |
| 2026-09-04T21:13:44.2415412Z | 2026-09-04T21:13:47.5110095Z | Documenting stage2 book redirect pages (stage1:aarch64-pc-windows-msvc -> stage2:arm64ec-pc-windows-msvc) | 0.054 | 12073 |
| 2026-09-04T21:13:47.5141418Z | 2026-09-04T21:13:48.7888596Z | Documenting stage2 standalone (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.021 | 12077 |
| 2026-09-04T21:13:48.7902880Z | 2026-09-04T21:13:50.0622120Z | Documenting stage2 standalone (stage1:aarch64-pc-windows-msvc -> stage2:arm64ec-pc-windows-msvc) | 0.021 | 12081 |
| 2026-09-04T21:13:50.0755849Z | 2026-09-04T21:16:54.8372340Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage1 -> stage1, aarch64-pc-windows-msvc) | 3.079 | 12085 |
| 2026-09-04T21:16:54.8410730Z | 2026-09-04T21:19:53.6831971Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage1:aarch64-pc-windows-msvc -> stage1:arm64ec-pc-windows-msvc) | 2.981 | 12137 |
| 2026-09-04T21:19:53.6994801Z | 2026-09-04T21:31:19.2357471Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 11.426 | 12194 |
| 2026-09-04T21:31:19.2410162Z | 2026-09-04T21:31:20.3777440Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.019 | 12805 |
| 2026-09-04T21:31:20.3886058Z | 2026-09-04T21:32:33.7088121Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.222 | 12814 |
| 2026-09-04T21:32:33.7117921Z | 2026-09-04T21:32:50.4471656Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.279 | 12943 |
| 2026-09-04T21:32:50.4534110Z | 2026-09-04T21:34:00.0537029Z | Building stage2 error_index_generator (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.160 | 13021 |
| 2026-09-04T21:34:34.3119900Z | 2026-09-04T21:34:37.9991761Z | Building stage1 lint-docs (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.061 | 13461 |
| 2026-09-04T21:34:38.0494197Z | 2026-09-04T21:35:09.0400543Z | Running stage2 lint-docs (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.517 | 13492 |
| 2026-09-04T21:35:13.6647110Z | 2026-09-04T21:35:13.9292874Z | Documenting stage2 releases (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.004 | 13595 |
| 2026-09-04T21:35:13.9299678Z | 2026-09-04T21:35:14.1535023Z | Documenting stage2 releases (stage1:aarch64-pc-windows-msvc -> stage2:arm64ec-pc-windows-msvc) | 0.004 | 13599 |
| 2026-09-04T21:36:11.0217313Z | 2026-09-04T21:36:40.1956938Z | Building stage1 rust-installer (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.486 | 13604 |
| 2026-09-04T21:41:44.4979648Z | 2026-09-04T21:42:00.3903905Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.265 | 13693 |
| 2026-09-04T21:42:08.0230140Z | 2026-09-04T21:42:21.8421359Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage1:aarch64-pc-windows-msvc -> stage1:arm64ec-pc-windows-msvc) | 0.230 | 13731 |
| 2026-09-04T21:42:29.1254056Z | 2026-09-04T21:44:03.1175117Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.567 | 13774 |
| 2026-09-04T21:44:03.1399745Z | 2026-09-04T21:44:51.1851564Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.801 | 13952 |
| 2026-09-04T21:44:51.2758379Z | 2026-09-04T21:49:43.3002906Z | Vendoring sources to "C:\\a\\rust\\rust" | 4.867 | 14153 |
| 2026-09-04T21:49:43.3017090Z | 2026-09-04T21:49:43.3033205Z | generate-copyright | 0.000 | 16740 |
| 2026-09-04T21:49:43.3033803Z | 2026-09-04T21:50:30.9876483Z | Building stage1 generate-copyright (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.795 | 16744 |
| 2026-09-04T21:50:30.9885692Z | 2026-09-04T21:50:36.8430719Z | generate-copyright (continued) | 0.098 | 16889 |
| 2026-09-04T21:53:35.4735135Z | 2026-09-04T21:53:38.1937060Z | Vendoring sources to "C:\\a\\rust\\rust\\build\\tmp\\tarball\\rust-src\\image\\lib/rustlib/src/rust" | 0.045 | 21266 |
| 2026-09-04T21:53:51.9012656Z | 2026-09-04T21:59:56.3425707Z | Building stage2 cargo (stage1 -> stage2, aarch64-pc-windows-msvc) | 6.074 | 21307 |
| 2026-09-04T22:00:07.0629008Z | 2026-09-04T22:05:49.1584784Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-pc-windows-msvc) | 5.702 | 22028 |
| 2026-09-04T22:05:59.9994490Z | 2026-09-04T22:07:01.9722912Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.033 | 22527 |
| 2026-09-04T22:07:01.9762610Z | 2026-09-04T22:07:02.6010336Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.010 | 22702 |
| 2026-09-04T22:07:07.5916854Z | 2026-09-04T22:08:58.8285442Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.854 | 22817 |
| 2026-09-04T22:08:58.8340780Z | 2026-09-04T22:08:59.4677934Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.011 | 22983 |
| 2026-09-04T22:14:52.3518721Z | 2026-09-04T22:15:26.0051503Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage2 -> stage2, aarch64-pc-windows-msvc) | 0.561 | 23110 |
| 2026-09-04T22:31:39.5423735Z | 2026-09-04T22:31:39.7454238Z | sccache stats | 0.003 | 23190 |
| 2026-09-04T21:36:40.2534293Z | 2026-09-04T21:38:45.8280064Z | Dist rust-docs-beta-aarch64-pc-windows-msvc | 2.093 | 13684 |
| 2026-09-04T21:39:43.0063179Z | 2026-09-04T21:41:44.4868345Z | Dist rust-docs-beta-arm64ec-pc-windows-msvc | 2.025 | 13688 |
| 2026-09-04T21:42:00.4741229Z | 2026-09-04T21:42:08.0187584Z | Dist rust-docs-json-beta-aarch64-pc-windows-msvc | 0.126 | 13726 |
| 2026-09-04T21:42:21.9192517Z | 2026-09-04T21:42:29.1108738Z | Dist rust-docs-json-beta-arm64ec-pc-windows-msvc | 0.120 | 13764 |
| 2026-09-04T21:50:36.9340215Z | 2026-09-04T21:51:31.8146267Z | Dist rustc-beta-aarch64-pc-windows-msvc | 0.915 | 21241 |
| 2026-09-04T21:51:32.6486111Z | 2026-09-04T21:51:46.1456288Z | Dist rust-std-beta-aarch64-pc-windows-msvc | 0.225 | 21245 |
| 2026-09-04T21:51:46.2659078Z | 2026-09-04T21:51:58.8284030Z | Dist rust-std-beta-arm64ec-pc-windows-msvc | 0.209 | 21249 |
| 2026-09-04T21:52:05.3940898Z | 2026-09-04T21:53:32.2292758Z | Dist rustc-dev-beta-aarch64-pc-windows-msvc | 1.447 | 21253 |
| 2026-09-04T21:53:32.3173384Z | 2026-09-04T21:53:32.3792748Z | Dist rust-analysis-beta-aarch64-pc-windows-msvc | 0.001 | 21257 |
| 2026-09-04T21:53:32.4782448Z | 2026-09-04T21:53:32.5360155Z | Dist rust-analysis-beta-arm64ec-pc-windows-msvc | 0.001 | 21261 |
| 2026-09-04T21:53:38.2654080Z | 2026-09-04T21:53:51.8983542Z | Dist rust-src-beta | 0.227 | 21301 |
| 2026-09-04T21:59:56.4564988Z | 2026-09-04T22:00:07.0352441Z | Dist cargo-beta-aarch64-pc-windows-msvc | 0.176 | 22022 |
| 2026-09-04T22:05:49.2459461Z | 2026-09-04T22:05:59.9923010Z | Dist rust-analyzer-beta-aarch64-pc-windows-msvc | 0.179 | 22521 |
| 2026-09-04T22:07:02.6818828Z | 2026-09-04T22:07:07.5887319Z | Dist rustfmt-beta-aarch64-pc-windows-msvc | 0.082 | 22811 |
| 2026-09-04T22:08:59.5529039Z | 2026-09-04T22:09:07.4050144Z | Dist clippy-beta-aarch64-pc-windows-msvc | 0.131 | 23087 |
| 2026-09-04T22:09:07.5079213Z | 2026-09-04T22:09:47.3229991Z | Dist llvm-tools-beta-aarch64-pc-windows-msvc | 0.664 | 23093 |
| 2026-09-04T22:09:47.4198114Z | 2026-09-04T22:09:48.9636152Z | Dist llvm-bitcode-linker-beta-aarch64-pc-windows-msvc | 0.026 | 23097 |
| 2026-09-04T22:09:53.1583900Z | 2026-09-04T22:14:52.2397232Z | Dist rust-dev-beta-aarch64-pc-windows-msvc | 4.985 | 23103 |
| 2026-09-04T22:15:26.1004797Z | 2026-09-04T22:15:34.2217194Z | Dist rust-docs-json-beta-aarch64-pc-windows-msvc | 0.135 | 23163 |
| 2026-09-04T22:15:34.3002456Z | 2026-09-04T22:22:35.7216355Z | Dist rust-beta-aarch64-pc-windows-msvc | 7.024 | 23166 |
| 2026-09-04T22:26:03.5169109Z | 2026-09-04T22:31:30.8316969Z | MSI package | 5.455 | 23179 |
| 2026-09-04T22:31:31.0584480Z | 2026-09-04T22:31:39.2731480Z | Dist bootstrap-beta-aarch64-pc-windows-msvc | 0.137 | 23186 |

</details>

## [auto - aarch64-apple-macos-26-2: 101163499206](https://github.com/rust-lang/rust/actions/runs/33916006473/job/101163499206)

Run 33916006473; raw SHA256 `21d4e9bef7cc1d27101c50a2c657cbae5bef950b2d4adf767ecccdcf5d8f1967`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 27.354 |
| Build support | 3.916 |
| LLVM/LLD | 157.474 |
| Compiler | 19.333 |
| Tools | 20.313 |
| Libraries | 1.706 |
| Tests | 30.402 |
| Docs | 9.587 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-04T20:32:21.1777950Z | 2026-09-04T20:32:21.1843370Z | Run set +e | 0.000 | 1951 |
| 2026-09-04T20:32:21.2611550Z | 2026-09-04T20:32:21.4962470Z | Clock drift check | 0.004 | 1997 |
| 2026-09-04T20:32:27.4349070Z | 2026-09-04T20:32:27.4387390Z | Configure the build | 0.000 | 2003 |
| 2026-09-04T20:32:36.0945590Z | 2026-09-04T20:33:04.1398790Z | Building bootstrap | 0.467 | 2048 |
| 2026-09-04T20:33:27.2753980Z | 2026-09-04T20:33:27.2766810Z | Building LLVM for aarch64-apple-darwin | 0.000 | 2179 |
| 2026-09-04T20:33:28.2593380Z | 2026-09-04T20:33:28.2595930Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-apple-darwin) | 0.000 | 2181 |
| 2026-09-04T20:33:28.2598600Z | 2026-09-04T20:33:28.2599400Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-apple-darwin) | 0.000 | 2184 |
| 2026-09-04T20:33:28.2621880Z | 2026-09-04T20:33:28.2625670Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-apple-darwin) | 0.000 | 2186 |
| 2026-09-04T20:33:28.2648330Z | 2026-09-04T20:33:28.2649390Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-apple-darwin) | 0.000 | 2188 |
| 2026-09-04T20:33:28.2669250Z | 2026-09-04T20:33:28.2670200Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-apple-darwin) | 0.000 | 2190 |
| 2026-09-04T20:33:28.2675200Z | 2026-09-04T20:33:28.2675930Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-apple-darwin) | 0.000 | 2192 |
| 2026-09-04T20:33:28.2676670Z | 2026-09-04T20:33:28.2677420Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-apple-darwin) | 0.000 | 2194 |
| 2026-09-04T20:33:28.2678810Z | 2026-09-04T20:33:28.2679470Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-apple-darwin) | 0.000 | 2197 |
| 2026-09-04T20:33:28.2680120Z | 2026-09-04T20:33:28.2682480Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-apple-darwin) | 0.000 | 2199 |
| 2026-09-04T20:33:28.2683330Z | 2026-09-04T20:33:28.2683910Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-apple-darwin) | 0.000 | 2201 |
| 2026-09-04T20:33:28.2684460Z | 2026-09-04T20:33:28.2685000Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-apple-darwin) | 0.000 | 2203 |
| 2026-09-04T20:33:28.2688620Z | 2026-09-04T20:33:28.2689370Z | Building stage2 cargo (stage1 -> stage2, aarch64-apple-darwin) | 0.000 | 2206 |
| 2026-09-04T20:33:28.2690020Z | 2026-09-04T20:33:28.2690710Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-apple-darwin) | 0.000 | 2208 |
| 2026-09-04T20:33:28.2691380Z | 2026-09-04T20:33:28.2692540Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-apple-darwin) | 0.000 | 2210 |
| 2026-09-04T20:33:28.2707000Z | 2026-09-04T20:33:28.2707820Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, aarch64-apple-darwin) | 0.000 | 2212 |
| 2026-09-04T20:33:28.2739750Z | 2026-09-04T20:33:28.2814090Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-apple-darwin) | 0.000 | 2214 |
| 2026-09-04T20:33:28.2814900Z | 2026-09-04T20:33:28.2815590Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-apple-darwin) | 0.000 | 2216 |
| 2026-09-04T20:33:28.2816250Z | 2026-09-04T20:33:28.2816960Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-apple-darwin) | 0.000 | 2218 |
| 2026-09-04T20:33:28.2817580Z | 2026-09-04T20:33:28.2818250Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-apple-darwin) | 0.000 | 2220 |
| 2026-09-04T20:33:28.2932180Z | 2026-09-04T20:33:28.8069580Z | Display CPU and Memory information | 0.009 | 2223 |
| 2026-09-04T20:33:28.9359360Z | 2026-09-04T20:33:29.2361110Z | Building bootstrap | 0.005 | 2373 |
| 2026-09-04T20:33:41.6397520Z | 2026-09-04T20:34:45.5725630Z | Building stage1 tidy (stage0 -> stage1, aarch64-apple-darwin) | 1.066 | 2386 |
| 2026-09-04T20:38:21.4124080Z | 2026-09-04T23:02:16.3311070Z | Building LLVM for aarch64-apple-darwin | 143.915 | 3272 |
| 2026-09-04T23:02:16.4338510Z | 2026-09-04T23:05:40.9186250Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-apple-darwin) | 3.408 | 10350 |
| 2026-09-04T23:05:40.9416860Z | 2026-09-04T23:07:49.1667050Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-apple-darwin) | 2.137 | 10952 |
| 2026-09-04T23:07:49.1707120Z | 2026-09-04T23:21:22.6695160Z | Building LLD for aarch64-apple-darwin | 13.558 | 11046 |
| 2026-09-04T23:21:22.6958680Z | 2026-09-04T23:21:24.8137500Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-apple-darwin) | 0.035 | 11311 |
| 2026-09-04T23:21:24.8286760Z | 2026-09-04T23:22:42.6702900Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-apple-darwin) | 1.297 | 11320 |
| 2026-09-04T23:22:42.7301070Z | 2026-09-04T23:22:54.1263010Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-apple-darwin) | 0.190 | 11426 |
| 2026-09-04T23:22:55.0787230Z | 2026-09-04T23:25:06.0153480Z | Building sanitizers for aarch64-apple-darwin | 2.182 | 11501 |
| 2026-09-04T23:25:07.6873130Z | 2026-09-04T23:26:49.3579450Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-apple-darwin) | 1.695 | 12086 |
| 2026-09-04T23:26:49.3727020Z | 2026-09-04T23:42:42.2082250Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-apple-darwin) | 15.881 | 12156 |
| 2026-09-04T23:42:42.2172680Z | 2026-09-04T23:44:39.9449490Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-apple-darwin) | 1.962 | 12760 |
| 2026-09-04T23:44:39.9542780Z | 2026-09-04T23:44:40.7850980Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-apple-darwin) | 0.014 | 12854 |
| 2026-09-04T23:44:40.8088350Z | 2026-09-04T23:45:40.2087210Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-apple-darwin) | 0.990 | 12863 |
| 2026-09-04T23:45:40.2419290Z | 2026-09-04T23:45:48.0425130Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-apple-darwin) | 0.130 | 12990 |
| 2026-09-04T23:45:51.4720840Z | 2026-09-04T23:45:52.2275080Z | Build sysroot | 0.013 | 13072 |
| 2026-09-04T23:45:52.2275900Z | 2026-09-04T23:45:52.3574000Z | [BUILD] mini_core | 0.002 | 13076 |
| 2026-09-04T23:45:52.3651460Z | 2026-09-04T23:45:52.4084930Z | [BUILD] example | 0.001 | 13079 |
| 2026-09-04T23:45:52.4131780Z | 2026-09-04T23:45:52.5591230Z | [AOT] mini_core_hello_world | 0.002 | 13083 |
| 2026-09-04T23:45:52.5591820Z | 2026-09-04T23:45:53.4385950Z | Build sysroot | 0.015 | 13101 |
| 2026-09-04T23:45:53.4415120Z | 2026-09-04T23:45:53.5767250Z | [AOT] arbitrary_self_types_pointers_and_wrappers | 0.002 | 13105 |
| 2026-09-04T23:45:53.5821500Z | 2026-09-04T23:45:53.8420790Z | [AOT] std_example | 0.004 | 13109 |
| 2026-09-04T23:45:53.8421280Z | 2026-09-04T23:45:53.9840860Z | [AOT] dst_field_align | 0.002 | 13129 |
| 2026-09-04T23:45:53.9866960Z | 2026-09-04T23:45:54.1619190Z | [AOT] subslice-patterns-const-eval | 0.003 | 13132 |
| 2026-09-04T23:45:54.1619910Z | 2026-09-04T23:45:54.2943750Z | [AOT] track-caller-attribute | 0.002 | 13135 |
| 2026-09-04T23:45:54.2944200Z | 2026-09-04T23:45:54.4498740Z | [AOT] float-minmax-pass | 0.003 | 13138 |
| 2026-09-04T23:45:54.4499710Z | 2026-09-04T23:45:54.5683960Z | [AOT] issue-72793 | 0.002 | 13141 |
| 2026-09-04T23:45:54.5684640Z | 2026-09-04T23:45:54.6874730Z | [AOT] issue-59326 | 0.002 | 13144 |
| 2026-09-04T23:45:54.6907810Z | 2026-09-04T23:45:55.0002170Z | [AOT] neon | 0.005 | 13147 |
| 2026-09-04T23:45:55.0002760Z | 2026-09-04T23:45:55.1387090Z | [AOT] gen_block_iterate | 0.002 | 13150 |
| 2026-09-04T23:45:55.1407740Z | 2026-09-04T23:45:55.2548790Z | [AOT] raw-dylib | 0.002 | 13153 |
| 2026-09-04T23:45:55.2550510Z | 2026-09-04T23:47:05.6531320Z | [TEST] sysroot | 1.173 | 13156 |
| 2026-09-04T23:47:06.2293950Z | 2026-09-04T23:47:06.4990430Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-apple-darwin) | 0.004 | 13309 |
| 2026-09-04T23:47:06.5037800Z | 2026-09-04T23:48:27.0269350Z | Building stage1 rustdoc_tool_binary (stage0 -> stage1, aarch64-apple-darwin) | 1.342 | 13352 |
| 2026-09-04T23:48:27.0577980Z | 2026-09-04T23:54:34.6664810Z | Testing stage2 {rustc-main, rustc_abi, rustc_arena, rustc_ast, rustc_ast_ir, rustc_ast_lowering, rustc_ast_passes, rustc_ast_pretty, rustc_attr_ir, rustc_attr_parsing, rustc_baked_icu_data, rustc_borrowck, rustc_builtin_macros, rustc_codegen_llvm, rustc_codegen_ssa, rustc_const_eval, rustc_crate_store, rustc_data_structures, rustc_driver, rustc_driver_impl, rustc_error_codes, rustc_error_messages, rustc_errors, rustc_expand, rustc_feature, rustc_fs_util, rustc_graphviz, rustc_hashes, rustc_hir, rustc_hir_analysis, rustc_hir_id, rustc_hir_pretty, rustc_hir_typeck, rustc_incremental, rustc_index, rustc_index_macros, rustc_infer, rustc_interface, rustc_lexer, rustc_lint, rustc_lint_defs, rustc_llvm, rustc_log, rustc_macros, rustc_metadata, rustc_middle, rustc_mir_build, rustc_mir_dataflow, rustc_mir_transform, rustc_monomorphize, rustc_next_trait_solver, rustc_parse, rustc_parse_format, rustc_passes, rustc_pattern_analysis, rustc_privacy, rustc_proc_macro, rustc_public, rustc_public_bridge, rustc_query_impl, rustc_resolve, rustc_sanitizers, rustc_serialize, rustc_session, rustc_span, rustc_symbol_mangling, rustc_target, rustc_thread_pool, rustc_trait_selection, rustc_traits, rustc_transmute, rustc_ty_utils, rustc_ty_walk, rustc_type_ir, rustc_type_ir_macros, rustc_windows_rc} (aarch64-apple-darwin) | 6.127 | 13537 |
| 2026-09-04T23:54:34.6721520Z | 2026-09-04T23:56:26.0156740Z | Testing stage2 rustdoc (aarch64-apple-darwin) | 1.856 | 16876 |
| 2026-09-04T23:56:26.0177570Z | 2026-09-04T23:56:44.7883230Z | Testing stage2 rustdoc-json-types (aarch64-apple-darwin) | 0.313 | 17227 |
| 2026-09-04T23:56:44.7902810Z | 2026-09-04T23:56:52.5936000Z | Testing stage1 coverage-dump (aarch64-apple-darwin) | 0.130 | 17353 |
| 2026-09-04T23:56:52.5940090Z | 2026-09-04T23:56:58.1099630Z | Testing stage1 jsondoclint (aarch64-apple-darwin) | 0.092 | 17412 |
| 2026-09-04T23:56:58.1102580Z | 2026-09-04T23:56:58.8627240Z | Testing stage1 replace-version-placeholder (aarch64-apple-darwin) | 0.013 | 17475 |
| 2026-09-04T23:56:58.8631230Z | 2026-09-04T23:58:19.4574400Z | Testing stage1 remote-test-client (aarch64-apple-darwin) | 1.343 | 17611 |
| 2026-09-04T23:58:19.4608080Z | 2026-09-04T23:58:23.7394180Z | Testing stage1 linkchecker self tests (aarch64-apple-darwin) | 0.071 | 17660 |
| 2026-09-04T23:58:23.7416520Z | 2026-09-04T23:58:29.1380510Z | Building stage1 unstable-book-gen (stage0 -> stage1, aarch64-apple-darwin) | 0.090 | 17752 |
| 2026-09-04T23:58:30.4826460Z | 2026-09-04T23:59:08.7980320Z | Building stage1 rustbook (stage0 -> stage1, aarch64-apple-darwin) | 0.639 | 17891 |
| 2026-09-04T23:59:12.3319590Z | 2026-09-04T23:59:13.8553790Z | Documenting stage2 book redirect pages (stage1 -> stage2, aarch64-apple-darwin) | 0.025 | 18256 |
| 2026-09-04T23:59:13.8574850Z | 2026-09-04T23:59:14.4092700Z | Documenting stage2 standalone (stage1 -> stage2, aarch64-apple-darwin) | 0.009 | 18260 |
| 2026-09-04T23:59:14.4305690Z | 2026-09-05T00:00:05.9807150Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage1 -> stage1, aarch64-apple-darwin) | 0.859 | 18265 |
| 2026-09-05T00:00:05.9913250Z | 2026-09-05T00:01:11.4018470Z | Building stage2 error_index_generator (stage1 -> stage2, aarch64-apple-darwin) | 1.090 | 18334 |
| 2026-09-05T00:01:31.8780380Z | 2026-09-05T00:01:37.9543350Z | Building stage1 lint-docs (stage0 -> stage1, aarch64-apple-darwin) | 0.101 | 18666 |
| 2026-09-05T00:01:38.0016850Z | 2026-09-05T00:02:04.6310880Z | Running stage2 lint-docs (stage1 -> stage2, aarch64-apple-darwin) | 0.444 | 18699 |
| 2026-09-05T00:02:06.6282620Z | 2026-09-05T00:02:06.8773900Z | Documenting stage2 releases (stage1 -> stage2, aarch64-apple-darwin) | 0.004 | 18757 |
| 2026-09-05T00:02:06.8932160Z | 2026-09-05T00:02:07.2249890Z | Building stage1 linkchecker (stage0 -> stage1, aarch64-apple-darwin) | 0.006 | 18762 |
| 2026-09-05T00:02:07.2461960Z | 2026-09-05T00:02:58.9205500Z | Testing stage1 Linkcheck (aarch64-apple-darwin) | 0.861 | 18807 |
| 2026-09-05T00:02:58.9254720Z | 2026-09-05T00:03:00.3794600Z | Testing stage2 platform support check (aarch64-apple-darwin) | 0.024 | 18820 |
| 2026-09-05T00:03:00.3830330Z | 2026-09-05T00:19:42.5774340Z | Testing stage2 rust-analyzer (aarch64-apple-darwin) | 16.703 | 18828 |
| 2026-09-05T00:19:42.5812370Z | 2026-09-05T00:19:42.6189820Z | Testing stage2 error-index (aarch64-apple-darwin) | 0.001 | 28056 |
| 2026-09-05T00:19:42.6237570Z | 2026-09-05T00:19:44.1448940Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, aarch64-apple-darwin) | 0.025 | 28060 |
| 2026-09-05T00:20:36.1810890Z | 2026-09-05T00:20:41.8614390Z | Testing stage2 book rustdoc (aarch64-apple-darwin) | 0.095 | 29293 |
| 2026-09-05T00:20:41.8630770Z | 2026-09-05T00:20:55.6647530Z | Testing stage2 book unstable-book (aarch64-apple-darwin) | 0.230 | 29496 |
| 2026-09-05T00:20:55.6655340Z | 2026-09-05T00:21:02.1622500Z | Testing stage2 book rustc (aarch64-apple-darwin) | 0.108 | 30102 |
| 2026-09-05T00:21:02.2848390Z | 2026-09-05T00:21:23.9137210Z | Running stage2 lint-docs (stage1 -> stage2, aarch64-apple-darwin) | 0.360 | 30741 |
| 2026-09-05T00:21:25.7169870Z | 2026-09-05T00:21:28.5791600Z | Building stage1 rustdoc-themes (stage0 -> stage1, aarch64-apple-darwin) | 0.048 | 30760 |
| 2026-09-05T00:21:28.6756270Z | 2026-09-05T00:27:12.7563500Z | Documenting stage2 compiler{rustc-main, rustc_abi, rustc_arena, rustc_ast, rustc_ast_ir, rustc_ast_lowering, rustc_ast_passes, rustc_ast_pretty, rustc_attr_ir, rustc_attr_parsing, rustc_baked_icu_data, rustc_borrowck, rustc_builtin_macros, rustc_codegen_llvm, rustc_codegen_ssa, rustc_const_eval, rustc_crate_store, rustc_data_structures, rustc_driver, rustc_driver_impl, rustc_error_codes, rustc_error_messages, rustc_errors, rustc_expand, rustc_feature, rustc_fs_util, rustc_graphviz, rustc_hashes, rustc_hir, rustc_hir_analysis, rustc_hir_id, rustc_hir_pretty, rustc_hir_typeck, rustc_incremental, rustc_index, rustc_index_macros, rustc_infer, rustc_interface, rustc_lexer, rustc_lint, rustc_lint_defs, rustc_llvm, rustc_log, rustc_macros, rustc_metadata, rustc_middle, rustc_mir_build, rustc_mir_dataflow, rustc_mir_transform, rustc_monomorphize, rustc_next_trait_solver, rustc_parse, rustc_parse_format, rustc_passes, rustc_pattern_analysis, rustc_privacy, rustc_proc_macro, rustc_public, rustc_public_bridge, rustc_query_impl, rustc_resolve, rustc_sanitizers, rustc_serialize, rustc_session, rustc_span, rustc_symbol_mangling, rustc_target, rustc_thread_pool, rustc_trait_selection, rustc_traits, rustc_transmute, rustc_ty_utils, rustc_ty_walk, rustc_type_ir, rustc_type_ir_macros, rustc_windows_rc} (stage1 -> stage2, aarch64-apple-darwin) | 5.735 | 30776 |
| 2026-09-05T00:27:12.7598770Z | 2026-09-05T00:27:17.2842160Z | Building stage1 html-checker (stage0 -> stage1, aarch64-apple-darwin) | 0.075 | 31450 |
| 2026-09-05T00:29:58.5583200Z | 2026-09-05T00:32:03.2806300Z | Testing stage1 rust-installer (aarch64-apple-darwin) | 2.079 | 31479 |
| 2026-09-05T00:32:03.2856040Z | 2026-09-05T00:32:38.4783080Z | Testing stage3 test-float-parse (aarch64-apple-darwin) | 0.587 | 31568 |
| 2026-09-05T00:34:31.3140170Z | 2026-09-05T00:34:31.8701600Z | Building bootstrap | 0.009 | 31785 |
| 2026-09-05T00:34:49.3910900Z | 2026-09-05T00:34:50.5746940Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-apple-darwin) | 0.020 | 31805 |
| 2026-09-05T00:34:50.5980500Z | 2026-09-05T00:34:50.7725210Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-apple-darwin) | 0.003 | 32136 |
| 2026-09-05T00:34:50.7737370Z | 2026-09-05T00:34:50.9790160Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-apple-darwin) | 0.003 | 32193 |
| 2026-09-05T00:34:51.0224970Z | 2026-09-05T00:34:51.4134470Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-apple-darwin) | 0.007 | 32201 |
| 2026-09-05T00:34:51.4196600Z | 2026-09-05T00:34:51.7009090Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-apple-darwin) | 0.005 | 32273 |
| 2026-09-05T00:34:52.9117980Z | 2026-09-05T00:34:53.3345500Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-apple-darwin) | 0.007 | 32328 |
| 2026-09-05T00:34:53.3351730Z | 2026-09-05T00:45:50.6163970Z | Building stage2 cargo (stage1 -> stage2, aarch64-apple-darwin) | 10.955 | 32372 |
| 2026-09-05T00:45:50.6332380Z | 2026-09-05T00:45:52.0966610Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-apple-darwin) | 0.024 | 33116 |
| 2026-09-05T00:45:52.0993020Z | 2026-09-05T00:45:52.2887190Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-apple-darwin) | 0.003 | 33449 |
| 2026-09-05T00:45:52.3207410Z | 2026-09-05T00:45:52.4625130Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-apple-darwin) | 0.002 | 33504 |
| 2026-09-05T00:45:52.4769870Z | 2026-09-05T00:45:52.7504770Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-apple-darwin) | 0.005 | 33512 |
| 2026-09-05T00:45:52.7668980Z | 2026-09-05T00:45:52.9644970Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-apple-darwin) | 0.003 | 33584 |
| 2026-09-05T00:45:53.2302660Z | 2026-09-05T00:45:53.5316820Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, aarch64-apple-darwin) | 0.005 | 33643 |
| 2026-09-05T00:45:53.5584960Z | 2026-09-05T00:45:53.8380370Z | Building stage1 rustdoc_tool_binary (stage0 -> stage1, aarch64-apple-darwin) | 0.005 | 33752 |
| 2026-09-05T01:02:25.6842160Z | 2026-09-05T01:02:25.8654900Z | sccache stats | 0.003 | 38928 |

</details>

## [auto - aarch64-msvc-2: 101163499284](https://github.com/rust-lang/rust/actions/runs/33916006473/job/101163499284)

Run 33916006473; raw SHA256 `4f0e5dcfa14e0488da06e0b9a7024b17a1c9549ac089d033c7f7b4f7140d163d`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 6.835 |
| Build support | 1.243 |
| LLVM/LLD | 12.277 |
| Compiler | 31.560 |
| Tools | 11.388 |
| Libraries | 1.264 |
| Tests | 27.977 |
| Docs | 3.591 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-04T20:37:51.4812056Z | 2026-09-04T20:37:51.4874002Z | Run set +e | 0.000 | 2001 |
| 2026-09-04T20:37:54.1364459Z | 2026-09-04T20:37:54.4568932Z | Clock drift check | 0.005 | 2047 |
| 2026-09-04T20:37:56.2676437Z | 2026-09-04T20:37:56.2698229Z | Configure the build | 0.000 | 2053 |
| 2026-09-04T20:38:05.5884786Z | 2026-09-04T20:39:19.2296568Z | Building bootstrap | 1.227 | 2098 |
| 2026-09-04T20:39:20.7168339Z | 2026-09-04T20:39:20.7259504Z | Building LLVM for aarch64-pc-windows-msvc | 0.000 | 2278 |
| 2026-09-04T20:39:21.4588094Z | 2026-09-04T20:39:21.4601257Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2280 |
| 2026-09-04T20:39:21.4609851Z | 2026-09-04T20:39:21.4610804Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2283 |
| 2026-09-04T20:39:21.4618247Z | 2026-09-04T20:39:21.4638411Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2285 |
| 2026-09-04T20:39:21.4649834Z | 2026-09-04T20:39:21.4652221Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2287 |
| 2026-09-04T20:39:21.4658402Z | 2026-09-04T20:39:21.4659508Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2289 |
| 2026-09-04T20:39:21.4675298Z | 2026-09-04T20:39:21.4680552Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2291 |
| 2026-09-04T20:39:21.4685550Z | 2026-09-04T20:39:21.4690084Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2293 |
| 2026-09-04T20:39:21.4698038Z | 2026-09-04T20:39:21.4699005Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2296 |
| 2026-09-04T20:39:21.4704931Z | 2026-09-04T20:39:21.4708202Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2298 |
| 2026-09-04T20:39:21.4719216Z | 2026-09-04T20:39:21.4721752Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2300 |
| 2026-09-04T20:39:21.4725834Z | 2026-09-04T20:39:21.4728357Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2302 |
| 2026-09-04T20:39:21.4749711Z | 2026-09-04T20:39:21.4752998Z | Building stage2 cargo (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2305 |
| 2026-09-04T20:39:21.4757991Z | 2026-09-04T20:39:21.4760089Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2307 |
| 2026-09-04T20:39:21.4766202Z | 2026-09-04T20:39:21.4768335Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2309 |
| 2026-09-04T20:39:21.4776225Z | 2026-09-04T20:39:21.4779132Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2311 |
| 2026-09-04T20:39:21.4785834Z | 2026-09-04T20:39:21.4788440Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2313 |
| 2026-09-04T20:39:21.4795824Z | 2026-09-04T20:39:21.4798107Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2315 |
| 2026-09-04T20:39:21.4804275Z | 2026-09-04T20:39:21.4807327Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2317 |
| 2026-09-04T20:39:21.4813098Z | 2026-09-04T20:39:21.4816448Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2319 |
| 2026-09-04T20:39:21.5144506Z | 2026-09-04T20:39:21.7810358Z | Display CPU and Memory information | 0.004 | 2322 |
| 2026-09-04T20:39:24.8181480Z | 2026-09-04T20:39:25.0126783Z | Building bootstrap | 0.003 | 2430 |
| 2026-09-04T20:39:26.5405945Z | 2026-09-04T20:40:25.9325446Z | Building stage1 tidy (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.990 | 2442 |
| 2026-09-04T20:44:39.9534008Z | 2026-09-04T20:56:27.2443504Z | Building LLVM for aarch64-pc-windows-msvc | 11.788 | 3367 |
| 2026-09-04T20:56:27.3494064Z | 2026-09-04T21:09:27.0228383Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 12.995 | 10539 |
| 2026-09-04T21:09:27.0488760Z | 2026-09-04T21:11:35.3851334Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-pc-windows-msvc) | 2.139 | 11149 |
| 2026-09-04T21:11:35.3962170Z | 2026-09-04T21:12:04.6956157Z | Building LLD for aarch64-pc-windows-msvc | 0.488 | 11243 |
| 2026-09-04T21:12:07.5361906Z | 2026-09-04T21:12:08.6846307Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.019 | 11484 |
| 2026-09-04T21:12:08.7015832Z | 2026-09-04T21:13:13.5998198Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.082 | 11493 |
| 2026-09-04T21:13:13.6065191Z | 2026-09-04T21:13:29.0011839Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.257 | 11602 |
| 2026-09-04T21:13:29.0386324Z | 2026-09-04T21:14:44.4684120Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 1.257 | 11685 |
| 2026-09-04T21:14:44.5213295Z | 2026-09-04T21:33:18.4492100Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 18.565 | 11738 |
| 2026-09-04T21:33:18.4546565Z | 2026-09-04T21:36:25.1860838Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-pc-windows-msvc) | 3.112 | 12348 |
| 2026-09-04T21:36:25.1891668Z | 2026-09-04T21:36:26.5559189Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.023 | 12442 |
| 2026-09-04T21:36:26.5649653Z | 2026-09-04T21:37:57.7176762Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.519 | 12451 |
| 2026-09-04T21:37:57.7204215Z | 2026-09-04T21:38:19.6987455Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.366 | 12580 |
| 2026-09-04T21:38:19.7174484Z | 2026-09-04T21:38:20.0973189Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.006 | 12673 |
| 2026-09-04T21:38:20.1023605Z | 2026-09-04T21:40:09.3217127Z | Building stage1 rustdoc_tool_binary (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.820 | 12706 |
| 2026-09-04T21:40:09.3378511Z | 2026-09-04T21:45:12.6718487Z | Testing stage2 {rustc-main, rustc_abi, rustc_arena, rustc_ast, rustc_ast_ir, rustc_ast_lowering, rustc_ast_passes, rustc_ast_pretty, rustc_attr_ir, rustc_attr_parsing, rustc_baked_icu_data, rustc_borrowck, rustc_builtin_macros, rustc_codegen_llvm, rustc_codegen_ssa, rustc_const_eval, rustc_crate_store, rustc_data_structures, rustc_driver, rustc_driver_impl, rustc_error_codes, rustc_error_messages, rustc_errors, rustc_expand, rustc_feature, rustc_fs_util, rustc_graphviz, rustc_hashes, rustc_hir, rustc_hir_analysis, rustc_hir_id, rustc_hir_pretty, rustc_hir_typeck, rustc_incremental, rustc_index, rustc_index_macros, rustc_infer, rustc_interface, rustc_lexer, rustc_lint, rustc_lint_defs, rustc_llvm, rustc_log, rustc_macros, rustc_metadata, rustc_middle, rustc_mir_build, rustc_mir_dataflow, rustc_mir_transform, rustc_monomorphize, rustc_next_trait_solver, rustc_parse, rustc_parse_format, rustc_passes, rustc_pattern_analysis, rustc_privacy, rustc_proc_macro, rustc_public, rustc_public_bridge, rustc_query_impl, rustc_resolve, rustc_sanitizers, rustc_serialize, rustc_session, rustc_span, rustc_symbol_mangling, rustc_target, rustc_thread_pool, rustc_trait_selection, rustc_traits, rustc_transmute, rustc_ty_utils, rustc_ty_walk, rustc_type_ir, rustc_type_ir_macros, rustc_windows_rc} (aarch64-pc-windows-msvc) | 5.056 | 12890 |
| 2026-09-04T21:45:12.6825646Z | 2026-09-04T21:48:09.1462622Z | Testing stage2 rustdoc (aarch64-pc-windows-msvc) | 2.941 | 16224 |
| 2026-09-04T21:48:09.1552523Z | 2026-09-04T21:48:47.3168773Z | Testing stage2 rustdoc-json-types (aarch64-pc-windows-msvc) | 0.636 | 16574 |
| 2026-09-04T21:48:47.3215164Z | 2026-09-04T21:48:59.6577979Z | Testing stage1 coverage-dump (aarch64-pc-windows-msvc) | 0.206 | 16700 |
| 2026-09-04T21:48:59.6596602Z | 2026-09-04T21:49:13.8427648Z | Testing stage1 jsondoclint (aarch64-pc-windows-msvc) | 0.236 | 16759 |
| 2026-09-04T21:49:13.8442073Z | 2026-09-04T21:49:15.6286279Z | Testing stage1 replace-version-placeholder (aarch64-pc-windows-msvc) | 0.030 | 16832 |
| 2026-09-04T21:49:15.6299682Z | 2026-09-04T21:49:26.5417208Z | Testing stage1 remote-test-client (aarch64-pc-windows-msvc) | 0.182 | 16967 |
| 2026-09-04T21:49:26.5435654Z | 2026-09-04T21:49:27.7888810Z | Testing stage2 platform support check (aarch64-pc-windows-msvc) | 0.021 | 17013 |
| 2026-09-04T21:49:27.7936559Z | 2026-09-04T22:06:37.8591675Z | Testing stage2 rust-analyzer (aarch64-pc-windows-msvc) | 17.168 | 17021 |
| 2026-09-04T22:06:37.8695873Z | 2026-09-04T22:08:01.4471511Z | Building stage2 error_index_generator (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.393 | 26255 |
| 2026-09-04T22:08:01.4482891Z | 2026-09-04T22:08:01.5011021Z | Testing stage2 error-index (aarch64-pc-windows-msvc) | 0.001 | 26461 |
| 2026-09-04T22:08:01.5337929Z | 2026-09-04T22:08:03.6032730Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.034 | 26472 |
| 2026-09-04T22:08:54.9055815Z | 2026-09-04T22:09:02.0479043Z | Testing stage2 book rustdoc (aarch64-pc-windows-msvc) | 0.119 | 27703 |
| 2026-09-04T22:09:02.0499005Z | 2026-09-04T22:09:23.4696437Z | Testing stage2 book unstable-book (aarch64-pc-windows-msvc) | 0.357 | 27906 |
| 2026-09-04T22:09:23.4718615Z | 2026-09-04T22:09:33.2446052Z | Testing stage2 book rustc (aarch64-pc-windows-msvc) | 0.163 | 28512 |
| 2026-09-04T22:09:33.3184174Z | 2026-09-04T22:09:36.9265488Z | Building stage1 lint-docs (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.060 | 29153 |
| 2026-09-04T22:09:36.9902744Z | 2026-09-04T22:10:08.5557288Z | Running stage2 lint-docs (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.526 | 29183 |
| 2026-09-04T22:10:08.5588567Z | 2026-09-04T22:11:23.8274311Z | Building stage1 rustbook (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.254 | 29188 |
| 2026-09-04T22:11:24.7394087Z | 2026-09-04T22:11:26.3060868Z | Building stage1 rustdoc-themes (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.026 | 29540 |
| 2026-09-04T22:11:26.4369585Z | 2026-09-04T22:11:53.5108369Z | Testing stage1 rust-installer (aarch64-pc-windows-msvc) | 0.451 | 29555 |
| 2026-09-04T22:11:53.5137105Z | 2026-09-04T22:12:39.6005799Z | Testing stage3 test-float-parse (aarch64-pc-windows-msvc) | 0.768 | 29650 |
| 2026-09-04T22:13:58.7660924Z | 2026-09-04T22:13:58.8931578Z | sccache stats | 0.002 | 29875 |

</details>

## [auto - dist-x86_64-msvc: 101163499345](https://github.com/rust-lang/rust/actions/runs/33916006473/job/101163499345)

Run 33916006473; raw SHA256 `ebccfa4442774dd79960e36972a74efc10abc3d9a84e0ba683556beb3c95856c`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 4.814 |
| Build support | 4.973 |
| LLVM/LLD | 33.123 |
| Compiler | 26.737 |
| Tools | 49.829 |
| Libraries | 0.819 |
| Tests | 31.139 |
| Docs | 5.040 |
| Packaging | 15.378 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-04T20:34:27.0979668Z | 2026-09-04T20:34:27.1009827Z | Run set +e | 0.000 | 2084 |
| 2026-09-04T20:34:27.9539245Z | 2026-09-04T20:34:28.1892711Z | Clock drift check | 0.004 | 2133 |
| 2026-09-04T20:34:28.8247010Z | 2026-09-04T20:34:28.8281645Z | Configure the build | 0.000 | 2139 |
| 2026-09-04T20:34:39.2657442Z | 2026-09-04T20:35:26.8671840Z | Building bootstrap | 0.793 | 2185 |
| 2026-09-04T20:35:27.7306762Z | 2026-09-04T20:35:27.7370509Z | Building LLVM for x86_64-pc-windows-msvc | 0.000 | 2365 |
| 2026-09-04T20:35:27.8131213Z | 2026-09-04T20:35:27.8143342Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2367 |
| 2026-09-04T20:35:27.8154310Z | 2026-09-04T20:35:27.8155113Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2370 |
| 2026-09-04T20:35:27.8163666Z | 2026-09-04T20:35:27.8170493Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2372 |
| 2026-09-04T20:35:27.8181539Z | 2026-09-04T20:35:27.8183582Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2374 |
| 2026-09-04T20:35:27.8188506Z | 2026-09-04T20:35:27.8191492Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2376 |
| 2026-09-04T20:35:27.8206638Z | 2026-09-04T20:35:27.8212056Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2378 |
| 2026-09-04T20:35:27.8216695Z | 2026-09-04T20:35:27.8220967Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2380 |
| 2026-09-04T20:35:27.8230314Z | 2026-09-04T20:35:27.8230955Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2383 |
| 2026-09-04T20:35:27.8237111Z | 2026-09-04T20:35:27.8240754Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2385 |
| 2026-09-04T20:35:27.8250907Z | 2026-09-04T20:35:27.8253291Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2387 |
| 2026-09-04T20:35:27.8258562Z | 2026-09-04T20:35:27.8260703Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2389 |
| 2026-09-04T20:35:27.8283523Z | 2026-09-04T20:35:27.8285889Z | Building stage2 cargo (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2392 |
| 2026-09-04T20:35:27.8290821Z | 2026-09-04T20:35:27.8293361Z | Building stage2 rust-analyzer (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2394 |
| 2026-09-04T20:35:27.8298715Z | 2026-09-04T20:35:27.8300790Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2396 |
| 2026-09-04T20:35:27.8308291Z | 2026-09-04T20:35:27.8310434Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2398 |
| 2026-09-04T20:35:27.8317295Z | 2026-09-04T20:35:27.8319469Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2400 |
| 2026-09-04T20:35:27.8325431Z | 2026-09-04T20:35:27.8327822Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2402 |
| 2026-09-04T20:35:27.8334164Z | 2026-09-04T20:35:27.8336509Z | Building stage2 rustfmt (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2404 |
| 2026-09-04T20:35:27.8342611Z | 2026-09-04T20:35:27.8344653Z | Building stage2 cargo-fmt (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2406 |
| 2026-09-04T20:35:27.8676869Z | 2026-09-04T20:35:28.1410169Z | Display CPU and Memory information | 0.005 | 2409 |
| 2026-09-04T20:35:28.2909498Z | 2026-09-04T20:35:28.4570495Z | Building bootstrap | 0.003 | 2637 |
| 2026-09-04T20:35:29.3419398Z | 2026-09-04T20:36:11.5848157Z | Building stage1 opt-dist (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.704 | 2648 |
| 2026-09-04T20:36:11.6152487Z | 2026-09-04T20:36:11.6240696Z | Environment values | 0.000 | 2899 |
| 2026-09-04T20:36:11.6241045Z | 2026-09-04T20:36:11.6322006Z | Printing bootstrap.toml | 0.000 | 3084 |
| 2026-09-04T20:36:11.6322985Z | 2026-09-04T20:38:11.5018199Z | Building rustc-perf | 1.998 | 3277 |
| 2026-09-04T20:38:11.6047372Z | 2026-09-04T20:38:11.7669353Z | Building bootstrap | 0.003 | 3855 |
| 2026-09-04T20:38:12.6475612Z | 2026-09-04T20:45:36.4097050Z | Building LLVM for x86_64-pc-windows-msvc | 7.396 | 3864 |
| 2026-09-04T20:45:36.4749845Z | 2026-09-04T20:54:20.3885791Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-pc-windows-msvc) | 8.732 | 11058 |
| 2026-09-04T20:54:20.3984360Z | 2026-09-04T20:58:26.6189627Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-pc-windows-msvc) | 4.104 | 11783 |
| 2026-09-04T20:58:26.6208682Z | 2026-09-04T20:58:42.2232962Z | Building LLD for x86_64-pc-windows-msvc | 0.260 | 11900 |
| 2026-09-04T20:58:42.2241328Z | 2026-09-04T20:58:43.0928592Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.014 | 12139 |
| 2026-09-04T20:58:43.1009582Z | 2026-09-04T20:59:32.8047855Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.828 | 12148 |
| 2026-09-04T20:59:32.8075558Z | 2026-09-04T20:59:50.3022612Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.292 | 12292 |
| 2026-09-04T20:59:50.3074926Z | 2026-09-04T21:00:37.8686197Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-pc-windows-msvc) | 0.793 | 12373 |
| 2026-09-04T21:00:37.8699679Z | 2026-09-04T21:08:51.6516540Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-pc-windows-msvc) | 8.230 | 12997 |
| 2026-09-04T21:08:51.6564141Z | 2026-09-04T21:12:59.0351991Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-pc-windows-msvc) | 4.123 | 13607 |
| 2026-09-04T21:12:59.0379279Z | 2026-09-04T21:12:59.8895421Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.014 | 13701 |
| 2026-09-04T21:12:59.8977663Z | 2026-09-04T21:13:49.9921842Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.835 | 13710 |
| 2026-09-04T21:13:49.9950681Z | 2026-09-04T21:14:07.6427741Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.294 | 13839 |
| 2026-09-04T21:14:07.6748545Z | 2026-09-04T21:16:58.2859495Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, x86_64-pc-windows-msvc) | 2.844 | 13922 |
| 2026-09-04T21:16:58.2895507Z | 2026-09-04T21:24:58.7402082Z | Building stage2 cargo (stage1 -> stage2, x86_64-pc-windows-msvc) | 8.008 | 14126 |
| 2026-09-04T21:24:58.7725621Z | 2026-09-04T21:38:33.7269626Z | Running benchmarks | 13.583 | 15052 |
| 2026-09-04T21:39:15.8103532Z | 2026-09-04T21:40:59.5777903Z | Running benchmarks | 1.729 | 15125 |
| 2026-09-04T21:41:16.7768464Z | 2026-09-04T21:41:17.0448323Z | Building bootstrap | 0.004 | 15180 |
| 2026-09-04T21:41:19.3564750Z | 2026-09-04T21:41:21.0555301Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.028 | 15204 |
| 2026-09-04T21:41:21.0654435Z | 2026-09-04T21:41:21.4140359Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.006 | 15537 |
| 2026-09-04T21:41:21.4168477Z | 2026-09-04T21:41:21.7683933Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.006 | 15594 |
| 2026-09-04T21:41:21.7766222Z | 2026-09-04T21:41:22.2604430Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.008 | 15602 |
| 2026-09-04T21:41:22.2635684Z | 2026-09-04T21:41:22.6925781Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.007 | 15674 |
| 2026-09-04T21:41:22.6979916Z | 2026-09-04T21:41:23.4832589Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-pc-windows-msvc) | 0.013 | 15728 |
| 2026-09-04T21:41:23.4834679Z | 2026-09-04T21:49:45.4191564Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-pc-windows-msvc) | 8.366 | 16326 |
| 2026-09-04T21:49:45.4234398Z | 2026-09-04T21:50:13.4244054Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.467 | 16905 |
| 2026-09-04T21:50:13.4268369Z | 2026-09-04T21:50:13.7915249Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.006 | 16961 |
| 2026-09-04T21:50:13.8003712Z | 2026-09-04T21:50:14.3015805Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.008 | 16969 |
| 2026-09-04T21:50:14.3045943Z | 2026-09-04T21:50:14.7467008Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.007 | 17041 |
| 2026-09-04T21:50:14.7801061Z | 2026-09-04T21:52:31.3022043Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, x86_64-pc-windows-msvc) | 2.275 | 17100 |
| 2026-09-04T21:52:31.3055907Z | 2026-09-04T21:58:59.3455015Z | Building stage2 cargo (stage1 -> stage2, x86_64-pc-windows-msvc) | 6.467 | 17266 |
| 2026-09-04T21:59:01.4052139Z | 2026-09-04T21:59:01.5830270Z | Building bootstrap | 0.003 | 18023 |
| 2026-09-04T21:59:02.9709786Z | 2026-09-04T22:11:48.3065665Z | Building LLVM for x86_64-pc-windows-msvc | 12.756 | 18032 |
| 2026-09-04T22:11:48.5425705Z | 2026-09-04T22:12:07.5502742Z | Building LLD for x86_64-pc-windows-msvc | 0.317 | 25238 |
| 2026-09-04T22:12:07.5515091Z | 2026-09-04T22:12:08.5211495Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.016 | 25477 |
| 2026-09-04T22:12:08.5287941Z | 2026-09-04T22:12:09.0627692Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.009 | 25485 |
| 2026-09-04T22:12:09.0655341Z | 2026-09-04T22:12:09.4914403Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.007 | 25557 |
| 2026-09-04T22:12:09.7754899Z | 2026-09-04T22:12:10.5790990Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.013 | 25626 |
| 2026-09-04T22:12:10.5872778Z | 2026-09-04T22:12:11.0629761Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.008 | 25634 |
| 2026-09-04T22:12:11.0659064Z | 2026-09-04T22:12:11.4981074Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.007 | 25706 |
| 2026-09-04T22:12:11.5566536Z | 2026-09-04T22:19:18.7338494Z | Running benchmarks | 7.120 | 25806 |
| 2026-09-04T22:19:27.4256355Z | 2026-09-04T22:19:27.6788968Z | Building bootstrap | 0.004 | 25865 |
| 2026-09-04T22:19:30.0564122Z | 2026-09-04T22:31:38.0154702Z | Building LLVM for x86_64-pc-windows-msvc | 12.133 | 25875 |
| 2026-09-04T22:31:38.1755994Z | 2026-09-04T22:31:53.8558201Z | Building LLD for x86_64-pc-windows-msvc | 0.261 | 33076 |
| 2026-09-04T22:31:53.8566309Z | 2026-09-04T22:31:54.2762389Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.007 | 33315 |
| 2026-09-04T22:31:54.2844853Z | 2026-09-04T22:31:54.7048269Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.007 | 33323 |
| 2026-09-04T22:31:54.7074716Z | 2026-09-04T22:31:55.0992201Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.007 | 33395 |
| 2026-09-04T22:31:55.1001587Z | 2026-09-04T22:31:55.8769659Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-pc-windows-msvc) | 0.013 | 33448 |
| 2026-09-04T22:31:55.8778699Z | 2026-09-04T22:32:54.1632350Z | Building stage1 unstable-book-gen (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.971 | 34051 |
| 2026-09-04T22:32:56.4702683Z | 2026-09-04T22:34:00.4120807Z | Building stage1 rustbook (stage0 -> stage1, x86_64-pc-windows-msvc) | 1.066 | 34286 |
| 2026-09-04T22:34:06.6656645Z | 2026-09-04T22:34:06.6730372Z | Documenting stage2 book redirect pages (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 34714 |
| 2026-09-04T22:34:06.6731038Z | 2026-09-04T22:37:09.1448942Z | Building stage1 rustdoc_tool_binary (stage0 -> stage1, x86_64-pc-windows-msvc) | 3.041 | 34718 |
| 2026-09-04T22:37:09.1450040Z | 2026-09-04T22:37:11.1082759Z | Documenting stage2 book redirect pages (stage1 -> stage2, x86_64-pc-windows-msvc) (continued) | 0.033 | 34900 |
| 2026-09-04T22:37:11.1089878Z | 2026-09-04T22:37:11.8186969Z | Documenting stage2 standalone (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.012 | 34906 |
| 2026-09-04T22:37:11.8214244Z | 2026-09-04T22:38:26.4780456Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage1 -> stage1, x86_64-pc-windows-msvc) | 1.244 | 34910 |
| 2026-09-04T22:38:26.4904666Z | 2026-09-04T22:39:49.3580164Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-pc-windows-msvc) | 1.381 | 34967 |
| 2026-09-04T22:39:49.3621049Z | 2026-09-04T22:40:17.0640096Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.462 | 35306 |
| 2026-09-04T22:40:17.0661303Z | 2026-09-04T22:40:17.4101639Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.006 | 35362 |
| 2026-09-04T22:40:17.4205716Z | 2026-09-04T22:40:17.8501951Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.007 | 35370 |
| 2026-09-04T22:40:17.8531854Z | 2026-09-04T22:40:18.2565961Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.007 | 35442 |
| 2026-09-04T22:40:18.2607819Z | 2026-09-04T22:41:02.0530849Z | Building stage2 error_index_generator (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.730 | 35496 |
| 2026-09-04T22:41:16.8436358Z | 2026-09-04T22:41:19.1141351Z | Building stage1 lint-docs (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.038 | 35829 |
| 2026-09-04T22:41:19.1617574Z | 2026-09-04T22:41:39.5352943Z | Running stage2 lint-docs (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.340 | 35860 |
| 2026-09-04T22:41:42.1739192Z | 2026-09-04T22:41:42.3793006Z | Documenting stage2 releases (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.003 | 35918 |
| 2026-09-04T22:42:10.0178754Z | 2026-09-04T22:42:38.5068939Z | Building stage1 rust-installer (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.475 | 35923 |
| 2026-09-04T22:43:55.1576728Z | 2026-09-04T22:44:09.3380752Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage1 -> stage1, x86_64-pc-windows-msvc) | 0.236 | 36006 |
| 2026-09-04T22:44:16.1367703Z | 2026-09-04T22:46:16.3828139Z | Building stage2 rustdoc_tool_binary (stage1 -> stage2, x86_64-pc-windows-msvc) | 2.004 | 36047 |
| 2026-09-04T22:46:16.3883408Z | 2026-09-04T22:47:07.6450287Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.854 | 36156 |
| 2026-09-04T22:47:07.6982561Z | 2026-09-04T22:48:40.4067243Z | Vendoring sources to "C:\\a\\rust\\rust" | 1.545 | 36350 |
| 2026-09-04T22:48:40.4071310Z | 2026-09-04T22:48:40.4081949Z | generate-copyright | 0.000 | 38534 |
| 2026-09-04T22:48:40.4082456Z | 2026-09-04T22:49:19.2641550Z | Building stage1 generate-copyright (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.648 | 38538 |
| 2026-09-04T22:49:19.2642247Z | 2026-09-04T22:49:23.2546600Z | generate-copyright (continued) | 0.067 | 38683 |
| 2026-09-04T22:51:24.3724731Z | 2026-09-04T22:51:25.3672431Z | Vendoring sources to "C:\\a\\rust\\rust\\build\\tmp\\tarball\\rust-src\\image\\lib/rustlib/src/rust" | 0.017 | 43054 |
| 2026-09-04T22:51:36.4633295Z | 2026-09-04T22:51:37.7912540Z | Building stage2 cargo (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.022 | 43095 |
| 2026-09-04T22:51:46.6550405Z | 2026-09-04T22:57:21.8950949Z | Building stage2 rust-analyzer (stage1 -> stage2, x86_64-pc-windows-msvc) | 5.587 | 43490 |
| 2026-09-04T22:57:31.0413735Z | 2026-09-04T22:58:43.5325373Z | Building stage2 rustfmt (stage1 -> stage2, x86_64-pc-windows-msvc) | 1.208 | 43994 |
| 2026-09-04T22:58:43.5354740Z | 2026-09-04T22:58:44.0363288Z | Building stage2 cargo-fmt (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.008 | 44180 |
| 2026-09-04T22:58:48.1110794Z | 2026-09-04T23:01:56.7148381Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-pc-windows-msvc) | 3.143 | 44295 |
| 2026-09-04T23:01:56.7179494Z | 2026-09-04T23:01:57.2576250Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.009 | 44463 |
| 2026-09-04T23:06:47.0485617Z | 2026-09-04T23:07:09.0442594Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage2 -> stage2, x86_64-pc-windows-msvc) | 0.367 | 44590 |
| 2026-09-04T23:15:02.3782770Z | 2026-09-04T23:15:33.9727208Z | Building bootstrap | 0.527 | 44828 |
| 2026-09-04T23:15:37.7596011Z | 2026-09-04T23:16:14.9750112Z | Building stage1 compiletest (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.620 | 44911 |
| 2026-09-04T23:16:15.0584650Z | 2026-09-04T23:16:32.6003503Z | Testing stage0 with compiletest suite=assembly-llvm mode=assembly (x86_64-pc-windows-msvc) | 0.292 | 45002 |
| 2026-09-04T23:16:32.6667872Z | 2026-09-04T23:16:50.5514662Z | Testing stage0 with compiletest suite=codegen-llvm mode=codegen (x86_64-pc-windows-msvc) | 0.298 | 45747 |
| 2026-09-04T23:16:50.6172544Z | 2026-09-04T23:16:51.7003120Z | Testing stage0 with compiletest suite=codegen-units mode=codegen-units (x86_64-pc-windows-msvc) | 0.018 | 46914 |
| 2026-09-04T23:16:51.7653428Z | 2026-09-04T23:16:51.8417393Z | Building test helpers for x86_64-pc-windows-msvc | 0.001 | 46967 |
| 2026-09-04T23:16:51.8420586Z | 2026-09-04T23:17:07.0253149Z | Testing stage0 with compiletest suite=incremental mode=incremental (x86_64-pc-windows-msvc) | 0.253 | 46970 |
| 2026-09-04T23:17:07.0914326Z | 2026-09-04T23:17:21.0192748Z | Testing stage0 with compiletest suite=mir-opt mode=mir-opt (x86_64-pc-windows-msvc) | 0.232 | 47157 |
| 2026-09-04T23:17:21.0857078Z | 2026-09-04T23:17:22.7763116Z | Testing stage0 with compiletest suite=pretty mode=pretty (x86_64-pc-windows-msvc) | 0.028 | 47572 |
| 2026-09-04T23:17:22.7768578Z | 2026-09-04T23:17:42.4608124Z | Building stage1 run_make_support (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.328 | 47693 |
| 2026-09-04T23:17:42.5285531Z | 2026-09-04T23:17:42.7300440Z | Testing stage0 with compiletest suite=run-make mode=run-make (x86_64-pc-windows-msvc) | 0.003 | 47727 |
| 2026-09-04T23:17:42.7968267Z | 2026-09-04T23:25:15.6555231Z | Testing stage0 with compiletest suite=ui mode=ui (x86_64-pc-windows-msvc) | 7.548 | 47736 |
| 2026-09-04T23:25:15.7297095Z | 2026-09-04T23:25:17.7754641Z | Testing stage0 with compiletest suite=crashes mode=crashes (x86_64-pc-windows-msvc) | 0.034 | 69772 |
| 2026-09-04T22:42:38.5561300Z | 2026-09-04T22:43:55.1558364Z | Dist rust-docs-beta-x86_64-pc-windows-msvc | 1.277 | 36001 |
| 2026-09-04T22:44:09.4008075Z | 2026-09-04T22:44:16.1279993Z | Dist rust-docs-json-beta-x86_64-pc-windows-msvc | 0.112 | 36039 |
| 2026-09-04T22:49:23.3257334Z | 2026-09-04T22:50:02.9912432Z | Dist rustc-beta-x86_64-pc-windows-msvc | 0.661 | 43035 |
| 2026-09-04T22:50:03.0786572Z | 2026-09-04T22:50:14.3029075Z | Dist rust-std-beta-x86_64-pc-windows-msvc | 0.187 | 43041 |
| 2026-09-04T22:50:15.6008723Z | 2026-09-04T22:51:22.7242206Z | Dist rustc-dev-beta-x86_64-pc-windows-msvc | 1.119 | 43045 |
| 2026-09-04T22:51:22.7899923Z | 2026-09-04T22:51:22.8320543Z | Dist rust-analysis-beta-x86_64-pc-windows-msvc | 0.001 | 43049 |
| 2026-09-04T22:51:25.4261556Z | 2026-09-04T22:51:36.4613691Z | Dist rust-src-beta | 0.184 | 43089 |
| 2026-09-04T22:51:37.8753915Z | 2026-09-04T22:51:46.6530992Z | Dist cargo-beta-x86_64-pc-windows-msvc | 0.146 | 43484 |
| 2026-09-04T22:57:21.9651120Z | 2026-09-04T22:57:31.0394434Z | Dist rust-analyzer-beta-x86_64-pc-windows-msvc | 0.151 | 43988 |
| 2026-09-04T22:58:44.1035703Z | 2026-09-04T22:58:48.1093352Z | Dist rustfmt-beta-x86_64-pc-windows-msvc | 0.067 | 44289 |
| 2026-09-04T23:01:57.3270967Z | 2026-09-04T23:02:03.7179116Z | Dist clippy-beta-x86_64-pc-windows-msvc | 0.107 | 44567 |
| 2026-09-04T23:02:03.7912097Z | 2026-09-04T23:02:38.2025339Z | Dist llvm-tools-beta-x86_64-pc-windows-msvc | 0.574 | 44573 |
| 2026-09-04T23:02:38.2696290Z | 2026-09-04T23:02:39.6244468Z | Dist llvm-bitcode-linker-beta-x86_64-pc-windows-msvc | 0.023 | 44577 |
| 2026-09-04T23:02:41.3707782Z | 2026-09-04T23:06:47.0438010Z | Dist rust-dev-beta-x86_64-pc-windows-msvc | 4.095 | 44583 |
| 2026-09-04T23:07:09.1203487Z | 2026-09-04T23:07:15.9827791Z | Dist rust-docs-json-beta-x86_64-pc-windows-msvc | 0.114 | 44643 |
| 2026-09-04T23:07:16.0506003Z | 2026-09-04T23:11:01.7653175Z | Dist rust-beta-x86_64-pc-windows-msvc | 3.762 | 44646 |
| 2026-09-04T23:12:00.3374159Z | 2026-09-04T23:14:30.7410619Z | MSI package | 2.507 | 44659 |
| 2026-09-04T23:14:30.8108488Z | 2026-09-04T23:14:40.0253335Z | Dist reproducible-artifacts-beta-x86_64-pc-windows-msvc | 0.154 | 44664 |
| 2026-09-04T23:14:40.0990570Z | 2026-09-04T23:14:48.4625116Z | Dist bootstrap-beta-x86_64-pc-windows-msvc | 0.139 | 44668 |

</details>

| opt-dist timer (nested) | Minutes |
|---|---:|
| Stage 1 (Rustc + rustdoc PGO) > Build PGO instrumented rustc and LLVM | 46.788 |
| Stage 1 (Rustc + rustdoc PGO) > Gather rustc profiles | 14.284 |
| Stage 1 (Rustc + rustdoc PGO) > Gather rustdoc profiles | 2.012 |
| Stage 1 (Rustc + rustdoc PGO) > Build PGO optimized rustc | 17.714 |
| Stage 1 (Rustc + rustdoc PGO) | 80.798 |
| Stage 2 (LLVM PGO) > Build PGO instrumented LLVM | 13.171 |
| Stage 2 (LLVM PGO) > Gather profiles | 7.220 |
| Stage 2 (LLVM PGO) | 20.465 |
| Stage 5 (final build) | 55.354 |
| Run tests | 11.493 |

## [auto - dist-aarch64-linux: 101293557894](https://github.com/rust-lang/rust/actions/runs/33961251131/job/101293557894)

Run 33961251131; raw SHA256 `ac79181932c04171f11f1682e4b8e0b63b9069a58203b44aa80f4e1deabe2421`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 3.203 |
| Build support | 1.472 |
| LLVM/LLD | 14.295 |
| Compiler | 9.867 |
| Tools | 24.062 |
| Libraries | 0.459 |
| Tests | 8.020 |
| Docs | 4.195 |
| Packaging | 4.377 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-05T10:42:09.1383393Z | 2026-09-05T10:42:09.1400866Z | Run set +e | 0.000 | 1441 |
| 2026-09-05T10:42:09.1740663Z | 2026-09-05T10:42:09.1823551Z | Image checksum input | 0.000 | 1482 |
| 2026-09-05T10:42:09.1824649Z | 2026-09-05T10:42:33.0724264Z | Building docker image for dist-aarch64-linux | 0.398 | 1901 |
| 2026-09-05T10:42:35.8935868Z | 2026-09-05T10:42:35.9284139Z | Clock drift check | 0.001 | 1978 |
| 2026-09-05T10:42:36.2438341Z | 2026-09-05T10:42:36.2454985Z | Configure the build | 0.000 | 1984 |
| 2026-09-05T10:42:44.7118324Z | 2026-09-05T10:42:54.6747002Z | Building bootstrap | 0.166 | 2039 |
| 2026-09-05T10:42:54.8595887Z | 2026-09-05T10:42:54.8596235Z | Building LLVM for aarch64-unknown-linux-gnu | 0.000 | 2170 |
| 2026-09-05T10:42:54.8598537Z | 2026-09-05T10:42:54.8599271Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2172 |
| 2026-09-05T10:42:54.8600192Z | 2026-09-05T10:42:54.8600632Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2175 |
| 2026-09-05T10:42:54.8602506Z | 2026-09-05T10:42:54.8602893Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2177 |
| 2026-09-05T10:42:54.8603629Z | 2026-09-05T10:42:54.8604039Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2179 |
| 2026-09-05T10:42:54.8604685Z | 2026-09-05T10:42:54.8605086Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2181 |
| 2026-09-05T10:42:54.8607168Z | 2026-09-05T10:42:54.8607552Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-unknown-linux-gnu) | 0.000 | 2183 |
| 2026-09-05T10:42:54.8608675Z | 2026-09-05T10:42:54.8609074Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2185 |
| 2026-09-05T10:42:54.8610270Z | 2026-09-05T10:42:54.8610743Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2188 |
| 2026-09-05T10:42:54.8611160Z | 2026-09-05T10:42:54.8611605Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2190 |
| 2026-09-05T10:42:54.8613055Z | 2026-09-05T10:42:54.8613444Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2192 |
| 2026-09-05T10:42:54.8614196Z | 2026-09-05T10:42:54.8614607Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2194 |
| 2026-09-05T10:42:54.8617789Z | 2026-09-05T10:42:54.8618169Z | Building stage2 cargo (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2197 |
| 2026-09-05T10:42:54.8619137Z | 2026-09-05T10:42:54.8619517Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2199 |
| 2026-09-05T10:42:54.8620857Z | 2026-09-05T10:42:54.8621294Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2201 |
| 2026-09-05T10:42:54.8622380Z | 2026-09-05T10:42:54.8622777Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2203 |
| 2026-09-05T10:42:54.8623716Z | 2026-09-05T10:42:54.8624096Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2205 |
| 2026-09-05T10:42:54.8632107Z | 2026-09-05T10:42:54.8632520Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2207 |
| 2026-09-05T10:42:54.8632831Z | 2026-09-05T10:42:54.8633191Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2209 |
| 2026-09-05T10:42:54.8633505Z | 2026-09-05T10:42:54.8633867Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2211 |
| 2026-09-05T10:42:54.8634172Z | 2026-09-05T10:42:54.8634523Z | Building stage2 miri (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2213 |
| 2026-09-05T10:42:54.8635024Z | 2026-09-05T10:42:54.8635406Z | Building stage2 cargo-miri (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 2215 |
| 2026-09-05T10:42:54.8710863Z | 2026-09-05T10:42:54.8769230Z | Display CPU and Memory information | 0.000 | 2218 |
| 2026-09-05T10:42:54.9289346Z | 2026-09-05T10:42:54.9648373Z | Building bootstrap | 0.001 | 2421 |
| 2026-09-05T10:42:55.1541613Z | 2026-09-05T10:43:09.0035357Z | Building stage1 opt-dist (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.231 | 2434 |
| 2026-09-05T10:43:09.0132822Z | 2026-09-05T10:43:09.0150724Z | Environment values | 0.000 | 2658 |
| 2026-09-05T10:43:09.0150972Z | 2026-09-05T10:43:09.0207985Z | Printing bootstrap.toml | 0.000 | 2712 |
| 2026-09-05T10:43:09.0208239Z | 2026-09-05T10:43:30.6661565Z | Building rustc-perf | 0.361 | 2947 |
| 2026-09-05T10:43:30.7200860Z | 2026-09-05T10:43:30.7581760Z | Building bootstrap | 0.001 | 3483 |
| 2026-09-05T10:43:30.9635332Z | 2026-09-05T10:44:47.0940169Z | Building LLVM for aarch64-unknown-linux-gnu | 1.269 | 3494 |
| 2026-09-05T10:44:47.1061150Z | 2026-09-05T10:49:07.5890447Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-unknown-linux-gnu) | 4.341 | 11067 |
| 2026-09-05T10:49:07.7764062Z | 2026-09-05T10:50:29.5583940Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-unknown-linux-gnu) | 1.363 | 11758 |
| 2026-09-05T10:50:29.5586853Z | 2026-09-05T10:50:32.7443841Z | Building LLD for aarch64-unknown-linux-gnu | 0.053 | 11877 |
| 2026-09-05T10:50:32.7447127Z | 2026-09-05T10:50:33.0023672Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.004 | 12149 |
| 2026-09-05T10:50:33.0028982Z | 2026-09-05T10:50:52.3278425Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.322 | 12158 |
| 2026-09-05T10:50:52.3284172Z | 2026-09-05T10:50:55.7878379Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.058 | 12297 |
| 2026-09-05T10:50:55.9336041Z | 2026-09-05T10:51:04.9129877Z | Building sanitizers for aarch64-unknown-linux-gnu | 0.150 | 12370 |
| 2026-09-05T10:51:04.9135184Z | 2026-09-05T10:51:32.2935482Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-unknown-linux-gnu) | 0.456 | 13129 |
| 2026-09-05T10:51:32.2999645Z | 2026-09-05T10:54:06.7101479Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-unknown-linux-gnu) | 2.574 | 13205 |
| 2026-09-05T10:54:06.7144652Z | 2026-09-05T10:55:53.8437072Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-unknown-linux-gnu) | 1.785 | 13797 |
| 2026-09-05T10:55:53.8441743Z | 2026-09-05T10:55:54.1600325Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.005 | 13891 |
| 2026-09-05T10:55:54.1605791Z | 2026-09-05T10:56:18.7864970Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.410 | 13900 |
| 2026-09-05T10:56:18.7870331Z | 2026-09-05T10:56:23.1134947Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.072 | 14027 |
| 2026-09-05T10:56:23.1152931Z | 2026-09-05T10:58:01.7854634Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-unknown-linux-gnu) | 1.645 | 14101 |
| 2026-09-05T10:58:01.7861422Z | 2026-09-05T11:02:12.6177428Z | Building stage2 cargo (stage1 -> stage2, aarch64-unknown-linux-gnu) | 4.181 | 14302 |
| 2026-09-05T11:02:12.6184019Z | 2026-09-05T11:04:11.9171296Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-unknown-linux-gnu) | 1.988 | 15191 |
| 2026-09-05T11:04:11.9179261Z | 2026-09-05T11:04:12.0387434Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 15375 |
| 2026-09-05T11:04:12.0524919Z | 2026-09-05T11:07:47.1443552Z | Running benchmarks | 3.585 | 15529 |
| 2026-09-05T11:08:47.7449135Z | 2026-09-05T11:09:10.4585171Z | Running benchmarks | 0.379 | 15603 |
| 2026-09-05T11:09:18.0678727Z | 2026-09-05T11:10:00.1482222Z | Running benchmarks | 0.701 | 15657 |
| 2026-09-05T11:10:09.0322631Z | 2026-09-05T11:10:09.3169541Z | Building bootstrap | 0.005 | 15712 |
| 2026-09-05T11:10:09.8378238Z | 2026-09-05T11:10:11.4603062Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.027 | 15738 |
| 2026-09-05T11:10:11.6490025Z | 2026-09-05T11:10:11.9194840Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.005 | 16060 |
| 2026-09-05T11:10:11.9205989Z | 2026-09-05T11:10:11.9974574Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.001 | 16117 |
| 2026-09-05T11:10:11.9979803Z | 2026-09-05T11:10:12.3423392Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.006 | 16125 |
| 2026-09-05T11:10:12.3429008Z | 2026-09-05T11:10:12.4941808Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.003 | 16197 |
| 2026-09-05T11:10:12.7375259Z | 2026-09-05T11:10:12.9049458Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-unknown-linux-gnu) | 0.003 | 16249 |
| 2026-09-05T11:10:12.9114380Z | 2026-09-05T11:13:08.4249858Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-unknown-linux-gnu) | 2.925 | 16291 |
| 2026-09-05T11:13:08.6237635Z | 2026-09-05T11:13:23.0303542Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.240 | 16851 |
| 2026-09-05T11:13:23.0307912Z | 2026-09-05T11:13:23.1060453Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.001 | 16907 |
| 2026-09-05T11:13:23.1065933Z | 2026-09-05T11:13:23.3813964Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.005 | 16915 |
| 2026-09-05T11:13:23.3819236Z | 2026-09-05T11:13:23.5130173Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 16987 |
| 2026-09-05T11:13:23.5147157Z | 2026-09-05T11:14:42.3512697Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-unknown-linux-gnu) | 1.314 | 17042 |
| 2026-09-05T11:14:42.3524834Z | 2026-09-05T11:17:52.9097918Z | Building stage2 cargo (stage1 -> stage2, aarch64-unknown-linux-gnu) | 3.176 | 17211 |
| 2026-09-05T11:17:52.9105427Z | 2026-09-05T11:19:31.1988287Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-unknown-linux-gnu) | 1.638 | 17919 |
| 2026-09-05T11:19:31.1995737Z | 2026-09-05T11:19:31.3308400Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 18089 |
| 2026-09-05T11:19:31.9019077Z | 2026-09-05T11:19:31.9614253Z | Building bootstrap | 0.001 | 18248 |
| 2026-09-05T11:19:32.1638246Z | 2026-09-05T11:23:03.0752668Z | Building LLVM for aarch64-unknown-linux-gnu | 3.515 | 18259 |
| 2026-09-05T11:23:03.0882800Z | 2026-09-05T11:23:11.4167278Z | Building LLD for aarch64-unknown-linux-gnu | 0.139 | 25847 |
| 2026-09-05T11:23:11.4170671Z | 2026-09-05T11:23:11.4907847Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.001 | 26123 |
| 2026-09-05T11:23:11.4913414Z | 2026-09-05T11:23:11.5939412Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.002 | 26131 |
| 2026-09-05T11:23:11.5944954Z | 2026-09-05T11:23:11.6894276Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.002 | 26203 |
| 2026-09-05T11:23:11.8458365Z | 2026-09-05T11:23:11.9203946Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.001 | 26270 |
| 2026-09-05T11:23:11.9209443Z | 2026-09-05T11:23:12.0102056Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.001 | 26278 |
| 2026-09-05T11:23:12.0107382Z | 2026-09-05T11:23:12.0940290Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.001 | 26350 |
| 2026-09-05T11:23:12.1052677Z | 2026-09-05T11:25:15.3440545Z | Running benchmarks | 2.054 | 26404 |
| 2026-09-05T11:25:57.6277502Z | 2026-09-05T11:25:58.0136768Z | Building bootstrap | 0.006 | 26507 |
| 2026-09-05T11:25:58.8249969Z | 2026-09-05T11:35:10.6231430Z | Building LLVM for aarch64-unknown-linux-gnu | 9.197 | 26519 |
| 2026-09-05T11:35:11.2467016Z | 2026-09-05T11:35:18.5951018Z | Building LLD for aarch64-unknown-linux-gnu | 0.122 | 34102 |
| 2026-09-05T11:35:18.5954104Z | 2026-09-05T11:35:18.8110976Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.004 | 34378 |
| 2026-09-05T11:35:18.8116206Z | 2026-09-05T11:35:19.1579529Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.006 | 34386 |
| 2026-09-05T11:35:19.1585340Z | 2026-09-05T11:35:19.3201162Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.003 | 34458 |
| 2026-09-05T11:35:19.6878754Z | 2026-09-05T11:35:32.4293951Z | Building stage1 unstable-book-gen (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.212 | 34518 |
| 2026-09-05T11:35:34.9779275Z | 2026-09-05T11:35:52.2259845Z | Building stage1 rustbook (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.287 | 34750 |
| 2026-09-05T11:35:56.8795787Z | 2026-09-05T11:35:56.8819898Z | Documenting stage2 book redirect pages (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 35177 |
| 2026-09-05T11:35:56.8820260Z | 2026-09-05T11:37:00.0716935Z | Building stage1 rustdoc-tool-binary (stage0 -> stage1, aarch64-unknown-linux-gnu) | 1.053 | 35181 |
| 2026-09-05T11:37:00.0718480Z | 2026-09-05T11:37:00.6899609Z | Documenting stage2 book redirect pages (stage1 -> stage2, aarch64-unknown-linux-gnu) (continued) | 0.010 | 35368 |
| 2026-09-05T11:37:00.6901738Z | 2026-09-05T11:37:00.9250790Z | Documenting stage2 standalone (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.004 | 35374 |
| 2026-09-05T11:37:00.9255562Z | 2026-09-05T11:37:17.1251778Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage1 -> stage1, aarch64-unknown-linux-gnu) | 0.270 | 35378 |
| 2026-09-05T11:37:17.1276614Z | 2026-09-05T11:38:00.7317160Z | Documenting stage2 compiler{rustc-main, rustc_abi, rustc_arena, rustc_ast, rustc_ast_ir, rustc_ast_lowering, rustc_ast_passes, rustc_ast_pretty, rustc_attr_ir, rustc_attr_parsing, rustc_baked_icu_data, rustc_borrowck, rustc_builtin_macros, rustc_codegen_llvm, rustc_codegen_ssa, rustc_const_eval, rustc_crate_store, rustc_data_structures, rustc_driver, rustc_driver_impl, rustc_error_codes, rustc_error_messages, rustc_errors, rustc_expand, rustc_feature, rustc_fs_util, rustc_graphviz, rustc_hashes, rustc_hir, rustc_hir_analysis, rustc_hir_id, rustc_hir_pretty, rustc_hir_typeck, rustc_incremental, rustc_index, rustc_index_macros, rustc_infer, rustc_interface, rustc_lexer, rustc_lint, rustc_lint_defs, rustc_llvm, rustc_log, rustc_macros, rustc_metadata, rustc_middle, rustc_mir_build, rustc_mir_dataflow, rustc_mir_transform, rustc_monomorphize, rustc_next_trait_solver, rustc_parse, rustc_parse_format, rustc_passes, rustc_pattern_analysis, rustc_privacy, rustc_proc_macro, rustc_public, rustc_public_bridge, rustc_query_impl, rustc_resolve, rustc_sanitizers, rustc_serialize, rustc_session, rustc_span, rustc_structures, rustc_symbol_mangling, rustc_target, rustc_thread_pool, rustc_trait_selection, rustc_traits, rustc_transmute, rustc_ty_utils, rustc_ty_walk, rustc_type_ir, rustc_type_ir_macros, rustc_windows_rc} (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.727 | 35447 |
| 2026-09-05T11:38:01.2018352Z | 2026-09-05T11:38:01.2811880Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.001 | 36126 |
| 2026-09-05T11:38:01.2817375Z | 2026-09-05T11:38:01.6571175Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.006 | 36134 |
| 2026-09-05T11:38:01.6576567Z | 2026-09-05T11:38:01.8240631Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.003 | 36206 |
| 2026-09-05T11:38:01.8251488Z | 2026-09-05T11:38:12.8862508Z | Documenting stage2 rustdoc (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.184 | 36253 |
| 2026-09-05T11:38:12.8870873Z | 2026-09-05T11:38:20.5760547Z | Documenting stage2 rustfmt (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.128 | 36444 |
| 2026-09-05T11:38:20.5766595Z | 2026-09-05T11:38:32.6501300Z | Building stage2 error_index_generator (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.201 | 36629 |
| 2026-09-05T11:38:55.4599682Z | 2026-09-05T11:38:58.1403420Z | Building stage1 lint-docs (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.045 | 36966 |
| 2026-09-05T11:38:58.1450219Z | 2026-09-05T11:39:11.1210199Z | Running stage2 lint-docs (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.216 | 37000 |
| 2026-09-05T11:39:11.6136989Z | 2026-09-05T11:39:57.0936913Z | Documenting stage2 cargo (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.758 | 37013 |
| 2026-09-05T11:39:57.5240704Z | 2026-09-05T11:40:00.4892868Z | Documenting stage2 clippy (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.049 | 37841 |
| 2026-09-05T11:40:00.6168635Z | 2026-09-05T11:40:00.6191292Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.000 | 37884 |
| 2026-09-05T11:40:00.6191669Z | 2026-09-05T11:40:18.0846219Z | Documenting stage2 miri (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.291 | 37887 |
| 2026-09-05T11:40:18.0846645Z | 2026-09-05T11:40:18.0848969Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, aarch64-unknown-linux-gnu) (continued) | 0.000 | 38051 |
| 2026-09-05T11:40:18.0849296Z | 2026-09-05T11:40:24.3505576Z | Documenting stage2 tidy (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.104 | 38055 |
| 2026-09-05T11:40:24.3505994Z | 2026-09-05T11:40:24.3508427Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, aarch64-unknown-linux-gnu) (continued) | 0.000 | 38272 |
| 2026-09-05T11:40:24.3508835Z | 2026-09-05T11:40:34.3805988Z | Documenting stage2 bootstrap (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.167 | 38276 |
| 2026-09-05T11:40:34.3806408Z | 2026-09-05T11:40:34.3809156Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, aarch64-unknown-linux-gnu) (continued) | 0.000 | 38441 |
| 2026-09-05T11:40:34.3809576Z | 2026-09-05T11:40:35.2132540Z | Documenting stage2 buildhelper (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.014 | 38445 |
| 2026-09-05T11:40:35.2132953Z | 2026-09-05T11:40:35.2135266Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, aarch64-unknown-linux-gnu) (continued) | 0.000 | 38452 |
| 2026-09-05T11:40:35.2135714Z | 2026-09-05T11:40:39.6604655Z | Documenting stage2 compiletest (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.074 | 38456 |
| 2026-09-05T11:40:39.6605083Z | 2026-09-05T11:40:39.6607310Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, aarch64-unknown-linux-gnu) (continued) | 0.000 | 38598 |
| 2026-09-05T11:40:39.6607665Z | 2026-09-05T11:40:44.1825640Z | Documenting stage2 runmakesupport (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.075 | 38602 |
| 2026-09-05T11:40:44.1826127Z | 2026-09-05T11:40:47.2728803Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, aarch64-unknown-linux-gnu) (continued) | 0.052 | 38685 |
| 2026-09-05T11:40:47.5949011Z | 2026-09-05T11:40:47.6544605Z | Documenting stage2 releases (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.001 | 38718 |
| 2026-09-05T11:40:48.2732634Z | 2026-09-05T11:40:59.7771137Z | Building stage1 rust-installer (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.192 | 38723 |
| 2026-09-05T11:41:51.8021810Z | 2026-09-05T11:41:58.3045449Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage1 -> stage1, aarch64-unknown-linux-gnu) | 0.108 | 38811 |
| 2026-09-05T11:42:02.3647970Z | 2026-09-05T11:42:02.8676539Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.008 | 38861 |
| 2026-09-05T11:42:02.8683263Z | 2026-09-05T11:42:20.2788679Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.290 | 38972 |
| 2026-09-05T11:42:20.2973889Z | 2026-09-05T11:42:32.0681574Z | Vendoring sources to "/checkout" | 0.196 | 39156 |
| 2026-09-05T11:42:32.0682870Z | 2026-09-05T11:42:32.0685982Z | generate-copyright | 0.000 | 41315 |
| 2026-09-05T11:42:32.0686350Z | 2026-09-05T11:42:36.7907957Z | Building stage1 generate-copyright (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.079 | 41319 |
| 2026-09-05T11:42:36.7908236Z | 2026-09-05T11:42:38.0908502Z | generate-copyright (continued) | 0.022 | 41450 |
| 2026-09-05T11:43:37.0462166Z | 2026-09-05T11:43:37.1276969Z | Vendoring sources to "/checkout/obj/build/tmp/tarball/rust-src/image/lib/rustlib/src/rust" | 0.001 | 45840 |
| 2026-09-05T11:43:43.2183100Z | 2026-09-05T11:43:44.8584094Z | Building stage2 cargo (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.027 | 45882 |
| 2026-09-05T11:43:52.5049810Z | 2026-09-05T11:45:58.2906646Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-unknown-linux-gnu) | 2.096 | 46281 |
| 2026-09-05T11:46:05.6053898Z | 2026-09-05T11:46:31.5347499Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.432 | 46774 |
| 2026-09-05T11:46:31.5353703Z | 2026-09-05T11:46:31.6364279Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 46949 |
| 2026-09-05T11:46:33.2062834Z | 2026-09-05T11:46:33.6579026Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.008 | 47060 |
| 2026-09-05T11:46:33.6585195Z | 2026-09-05T11:46:33.7622853Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.002 | 47163 |
| 2026-09-05T11:46:37.2646824Z | 2026-09-05T11:47:22.7212295Z | Building stage2 miri (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.758 | 47270 |
| 2026-09-05T11:47:22.7218559Z | 2026-09-05T11:47:28.7365701Z | Building stage2 cargo-miri (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.100 | 47509 |
| 2026-09-05T11:48:01.4146235Z | 2026-09-05T11:48:14.3115707Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage2 -> stage2, aarch64-unknown-linux-gnu) | 0.215 | 47604 |
| 2026-09-05T11:49:38.3590715Z | 2026-09-05T11:49:56.3939849Z | Building stage2 build-manifest (stage1 -> stage2, aarch64-unknown-linux-gnu) | 0.301 | 47686 |
| 2026-09-05T11:50:16.2182268Z | 2026-09-05T11:50:25.8951481Z | Building bootstrap | 0.161 | 48141 |
| 2026-09-05T11:50:26.4429883Z | 2026-09-05T11:50:34.8109017Z | Building stage1 compiletest (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.139 | 48208 |
| 2026-09-05T11:50:34.8156779Z | 2026-09-05T11:50:37.2220887Z | Testing stage0 with compiletest suite=assembly-llvm mode=assembly (aarch64-unknown-linux-gnu) | 0.040 | 48287 |
| 2026-09-05T11:50:37.2235285Z | 2026-09-05T11:50:39.5470053Z | Testing stage0 with compiletest suite=codegen-llvm mode=codegen (aarch64-unknown-linux-gnu) | 0.039 | 49068 |
| 2026-09-05T11:50:39.5484152Z | 2026-09-05T11:50:39.7184740Z | Testing stage0 with compiletest suite=codegen-units mode=codegen-units (aarch64-unknown-linux-gnu) | 0.003 | 50300 |
| 2026-09-05T11:50:39.7198593Z | 2026-09-05T11:50:39.7742943Z | Building test helpers for aarch64-unknown-linux-gnu | 0.001 | 50353 |
| 2026-09-05T11:50:39.7744229Z | 2026-09-05T11:50:43.8283974Z | Testing stage0 with compiletest suite=incremental mode=incremental (aarch64-unknown-linux-gnu) | 0.068 | 50355 |
| 2026-09-05T11:50:43.8298651Z | 2026-09-05T11:50:45.0286214Z | Testing stage0 with compiletest suite=mir-opt mode=mir-opt (aarch64-unknown-linux-gnu) | 0.020 | 50542 |
| 2026-09-05T11:50:45.0300724Z | 2026-09-05T11:50:45.3912430Z | Testing stage0 with compiletest suite=pretty mode=pretty (aarch64-unknown-linux-gnu) | 0.006 | 50959 |
| 2026-09-05T11:50:45.3927311Z | 2026-09-05T11:50:50.4777001Z | Building stage1 run_make_support (stage0 -> stage1, aarch64-unknown-linux-gnu) | 0.085 | 51080 |
| 2026-09-05T11:50:50.4779311Z | 2026-09-05T11:50:50.5211417Z | Testing stage0 with compiletest suite=run-make mode=run-make (aarch64-unknown-linux-gnu) | 0.001 | 51110 |
| 2026-09-05T11:50:50.5228004Z | 2026-09-05T11:51:49.8267985Z | Testing stage0 with compiletest suite=ui mode=ui (aarch64-unknown-linux-gnu) | 0.988 | 51119 |
| 2026-09-05T11:51:49.8286412Z | 2026-09-05T11:51:50.1395273Z | Testing stage0 with compiletest suite=crashes mode=crashes (aarch64-unknown-linux-gnu) | 0.005 | 73319 |
| 2026-09-05T11:51:50.1413606Z | 2026-09-05T11:51:58.0413275Z | Testing stage0 with compiletest suite=rustdoc-html mode=rustdoc-html (aarch64-unknown-linux-gnu) | 0.132 | 73528 |
| 2026-09-05T11:51:58.0525484Z | 2026-09-05T11:51:58.0548460Z | sccache stats | 0.000 | 74385 |
| 2026-09-05T11:51:58.0548705Z | 2026-09-05T11:51:58.1564500Z | Clock drift check | 0.002 | 74428 |
| 2026-09-05T11:40:59.7820816Z | 2026-09-05T11:41:18.9360150Z | Dist rust-docs-nightly-aarch64-unknown-linux-gnu | 0.319 | 38802 |
| 2026-09-05T11:41:19.4449958Z | 2026-09-05T11:41:51.8017890Z | Dist rustc-docs-nightly-aarch64-unknown-linux-gnu | 0.539 | 38806 |
| 2026-09-05T11:41:58.3098337Z | 2026-09-05T11:42:02.3640782Z | Dist rust-docs-json-nightly-aarch64-unknown-linux-gnu | 0.068 | 38853 |
| 2026-09-05T11:42:38.1037111Z | 2026-09-05T11:42:55.1395393Z | Dist rustc-nightly-aarch64-unknown-linux-gnu | 0.284 | 45819 |
| 2026-09-05T11:42:55.1469805Z | 2026-09-05T11:42:57.5451355Z | Dist rustc-codegen-cranelift-nightly-aarch64-unknown-linux-gnu | 0.040 | 45823 |
| 2026-09-05T11:42:57.5520830Z | 2026-09-05T11:43:05.2128039Z | Dist rust-std-nightly-aarch64-unknown-linux-gnu | 0.128 | 45827 |
| 2026-09-05T11:43:05.3613825Z | 2026-09-05T11:43:36.3165448Z | Dist rustc-dev-nightly-aarch64-unknown-linux-gnu | 0.516 | 45831 |
| 2026-09-05T11:43:36.3220557Z | 2026-09-05T11:43:36.3413047Z | Dist rust-analysis-nightly-aarch64-unknown-linux-gnu | 0.000 | 45835 |
| 2026-09-05T11:43:37.1329494Z | 2026-09-05T11:43:43.2178476Z | Dist rust-src-nightly | 0.101 | 45876 |
| 2026-09-05T11:43:44.8691000Z | 2026-09-05T11:43:52.5042694Z | Dist cargo-nightly-aarch64-unknown-linux-gnu | 0.127 | 46275 |
| 2026-09-05T11:45:58.2982144Z | 2026-09-05T11:46:05.6047698Z | Dist rust-analyzer-nightly-aarch64-unknown-linux-gnu | 0.122 | 46768 |
| 2026-09-05T11:46:31.6437427Z | 2026-09-05T11:46:33.2056492Z | Dist rustfmt-nightly-aarch64-unknown-linux-gnu | 0.026 | 47054 |
| 2026-09-05T11:46:33.7695349Z | 2026-09-05T11:46:37.2640384Z | Dist clippy-nightly-aarch64-unknown-linux-gnu | 0.058 | 47264 |
| 2026-09-05T11:47:28.7440550Z | 2026-09-05T11:47:30.7721477Z | Dist miri-nightly-aarch64-unknown-linux-gnu | 0.034 | 47583 |
| 2026-09-05T11:47:30.7792146Z | 2026-09-05T11:47:40.1671839Z | Dist llvm-tools-nightly-aarch64-unknown-linux-gnu | 0.156 | 47587 |
| 2026-09-05T11:47:40.1733296Z | 2026-09-05T11:47:40.5973344Z | Dist llvm-bitcode-linker-nightly-aarch64-unknown-linux-gnu | 0.007 | 47591 |
| 2026-09-05T11:47:41.6704336Z | 2026-09-05T11:48:01.4138293Z | Dist rust-dev-nightly-aarch64-unknown-linux-gnu | 0.329 | 47597 |
| 2026-09-05T11:48:14.3218021Z | 2026-09-05T11:48:18.4102154Z | Dist rust-docs-json-nightly-aarch64-unknown-linux-gnu | 0.068 | 47673 |
| 2026-09-05T11:48:18.4161152Z | 2026-09-05T11:49:25.6908079Z | Dist rust-nightly-aarch64-unknown-linux-gnu | 1.121 | 47676 |
| 2026-09-05T11:49:26.2630040Z | 2026-09-05T11:49:38.3586244Z | Dist reproducible-artifacts-nightly-aarch64-unknown-linux-gnu | 0.202 | 47680 |
| 2026-09-05T11:49:56.3995665Z | 2026-09-05T11:49:56.7987261Z | Dist build-manifest-nightly-aarch64-unknown-linux-gnu | 0.007 | 47808 |
| 2026-09-05T11:49:56.8042470Z | 2026-09-05T11:50:02.4415800Z | Dist bootstrap-nightly-aarch64-unknown-linux-gnu | 0.094 | 47812 |
| 2026-09-05T11:50:09.3157429Z | 2026-09-05T11:50:11.1540122Z | Dist enzyme-nightly-aarch64-unknown-linux-gnu | 0.031 | 47955 |

</details>

| opt-dist timer (nested) | Minutes |
|---|---:|
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Build PGO instrumented rustc and LLVM | 20.690 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather rustc profiles | 4.595 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather rustdoc profiles | 0.505 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather clippy profiles | 0.846 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Build PGO optimized rustc | 9.376 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) | 36.011 |
| Stage 2 (LLVM PGO) > Build PGO instrumented LLVM | 3.671 |
| Stage 2 (LLVM PGO) > Gather profiles | 2.730 |
| Stage 2 (LLVM PGO) | 6.436 |
| Stage 5 (final build) | 24.228 |
| Run tests | 1.781 |

## [auto - dist-x86_64-linux: 101293558080](https://github.com/rust-lang/rust/actions/runs/33961251131/job/101293558080)

Run 33961251131; raw SHA256 `7a5efc79cf79e4fd6b746293617888a385526dc2666e02cbb22946f798162d90`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 10.475 |
| Build support | 9.049 |
| LLVM/LLD | 15.155 |
| Compiler | 10.303 |
| Tools | 26.287 |
| Libraries | 0.491 |
| Tests | 16.968 |
| Docs | 4.133 |
| Packaging | 9.939 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-05T10:42:17.6916598Z | 2026-09-05T10:42:17.6933273Z | Run set +e | 0.000 | 1446 |
| 2026-09-05T10:42:17.7352400Z | 2026-09-05T10:42:17.7443162Z | Image checksum input | 0.000 | 1488 |
| 2026-09-05T10:42:17.7444003Z | 2026-09-05T10:42:38.3659103Z | Building docker image for dist-x86_64-linux | 0.344 | 1963 |
| 2026-09-05T10:42:41.0002546Z | 2026-09-05T10:42:41.0188133Z | Clock drift check | 0.000 | 2046 |
| 2026-09-05T10:42:41.3393357Z | 2026-09-05T10:42:41.3405536Z | Configure the build | 0.000 | 2052 |
| 2026-09-05T10:42:51.0665764Z | 2026-09-05T10:43:01.0163238Z | Building bootstrap | 0.166 | 2104 |
| 2026-09-05T10:43:01.1690388Z | 2026-09-05T10:43:01.1690698Z | Building LLVM for x86_64-unknown-linux-gnu | 0.000 | 2235 |
| 2026-09-05T10:43:01.1691029Z | 2026-09-05T10:43:01.1691360Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2237 |
| 2026-09-05T10:43:01.1692096Z | 2026-09-05T10:43:01.1692411Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2240 |
| 2026-09-05T10:43:01.1692686Z | 2026-09-05T10:43:01.1692975Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2242 |
| 2026-09-05T10:43:01.1693242Z | 2026-09-05T10:43:01.1693543Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2244 |
| 2026-09-05T10:43:01.1693819Z | 2026-09-05T10:43:01.1694122Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2246 |
| 2026-09-05T10:43:01.1694389Z | 2026-09-05T10:43:01.1694685Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-unknown-linux-gnu) | 0.000 | 2248 |
| 2026-09-05T10:43:01.1694964Z | 2026-09-05T10:43:01.1695258Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2250 |
| 2026-09-05T10:43:01.1695876Z | 2026-09-05T10:43:01.1696197Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2253 |
| 2026-09-05T10:43:01.1696447Z | 2026-09-05T10:43:01.1696732Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2255 |
| 2026-09-05T10:43:01.1696999Z | 2026-09-05T10:43:01.1697297Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2257 |
| 2026-09-05T10:43:01.1697560Z | 2026-09-05T10:43:01.1697864Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2259 |
| 2026-09-05T10:43:01.1698298Z | 2026-09-05T10:43:01.1698594Z | Building stage2 cargo (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2262 |
| 2026-09-05T10:43:01.1698857Z | 2026-09-05T10:43:01.1699153Z | Building stage2 rust-analyzer (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2264 |
| 2026-09-05T10:43:01.1700065Z | 2026-09-05T10:43:01.1700396Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2266 |
| 2026-09-05T10:43:01.1701362Z | 2026-09-05T10:43:01.1701758Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2268 |
| 2026-09-05T10:43:01.1702706Z | 2026-09-05T10:43:01.1703004Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2270 |
| 2026-09-05T10:43:01.1703882Z | 2026-09-05T10:43:01.1704182Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2272 |
| 2026-09-05T10:43:01.1704671Z | 2026-09-05T10:43:01.1705105Z | Building stage2 rustfmt (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2274 |
| 2026-09-05T10:43:01.1705569Z | 2026-09-05T10:43:01.1705866Z | Building stage2 cargo-fmt (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2276 |
| 2026-09-05T10:43:01.1706634Z | 2026-09-05T10:43:01.1706996Z | Building stage2 miri (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2278 |
| 2026-09-05T10:43:01.1707793Z | 2026-09-05T10:43:01.1708090Z | Building stage2 cargo-miri (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 2280 |
| 2026-09-05T10:43:01.1792037Z | 2026-09-05T10:43:01.1911909Z | Display CPU and Memory information | 0.000 | 2283 |
| 2026-09-05T10:43:01.2323893Z | 2026-09-05T10:43:01.2643724Z | Building bootstrap | 0.001 | 2794 |
| 2026-09-05T10:43:01.4247501Z | 2026-09-05T10:43:16.0809980Z | Building stage1 opt-dist (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.244 | 2807 |
| 2026-09-05T10:43:16.0913853Z | 2026-09-05T10:43:16.0926787Z | Environment values | 0.000 | 3031 |
| 2026-09-05T10:43:16.0926997Z | 2026-09-05T10:43:16.0966044Z | Printing bootstrap.toml | 0.000 | 3085 |
| 2026-09-05T10:43:16.0967143Z | 2026-09-05T10:43:38.4428912Z | Building rustc-perf | 0.372 | 3296 |
| 2026-09-05T10:43:38.4919358Z | 2026-09-05T10:43:38.5256924Z | Building bootstrap | 0.001 | 3835 |
| 2026-09-05T10:43:38.7011866Z | 2026-09-05T10:44:55.6104818Z | Building LLVM for x86_64-unknown-linux-gnu | 1.282 | 3846 |
| 2026-09-05T10:44:55.6220407Z | 2026-09-05T10:49:18.2726517Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-unknown-linux-gnu) | 4.378 | 11424 |
| 2026-09-05T10:49:18.4706347Z | 2026-09-05T10:50:41.0917416Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-unknown-linux-gnu) | 1.377 | 12116 |
| 2026-09-05T10:50:41.0920424Z | 2026-09-05T10:50:44.0426272Z | Building LLD for x86_64-unknown-linux-gnu | 0.049 | 12235 |
| 2026-09-05T10:50:44.0429873Z | 2026-09-05T10:50:44.2812233Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.004 | 12507 |
| 2026-09-05T10:50:44.2817388Z | 2026-09-05T10:51:00.5766028Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.272 | 12516 |
| 2026-09-05T10:51:00.5770694Z | 2026-09-05T10:51:03.9984778Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.057 | 12655 |
| 2026-09-05T10:51:04.1008290Z | 2026-09-05T10:51:12.6551907Z | Building sanitizers for x86_64-unknown-linux-gnu | 0.143 | 12728 |
| 2026-09-05T10:51:12.6558104Z | 2026-09-05T10:51:41.8282154Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-unknown-linux-gnu) | 0.486 | 13499 |
| 2026-09-05T10:51:41.8339773Z | 2026-09-05T10:54:30.1259175Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-unknown-linux-gnu) | 2.805 | 13575 |
| 2026-09-05T10:54:30.1277025Z | 2026-09-05T10:56:20.5815680Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-unknown-linux-gnu) | 1.841 | 14164 |
| 2026-09-05T10:56:20.5820678Z | 2026-09-05T10:56:20.8784421Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.005 | 14258 |
| 2026-09-05T10:56:20.8789183Z | 2026-09-05T10:56:43.4208995Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.376 | 14267 |
| 2026-09-05T10:56:43.4213967Z | 2026-09-05T10:56:47.8513099Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.074 | 14394 |
| 2026-09-05T10:56:47.8528549Z | 2026-09-05T10:58:26.7024139Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, x86_64-unknown-linux-gnu) | 1.647 | 14468 |
| 2026-09-05T10:58:26.7943148Z | 2026-09-05T11:02:36.6226000Z | Building stage2 cargo (stage1 -> stage2, x86_64-unknown-linux-gnu) | 4.164 | 14667 |
| 2026-09-05T11:02:36.6232444Z | 2026-09-05T11:04:37.8157201Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-unknown-linux-gnu) | 2.020 | 15556 |
| 2026-09-05T11:04:37.8162128Z | 2026-09-05T11:04:37.9229946Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.002 | 15740 |
| 2026-09-05T11:04:37.9323394Z | 2026-09-05T11:08:16.4640378Z | Running benchmarks | 3.642 | 15842 |
| 2026-09-05T11:09:22.8560799Z | 2026-09-05T11:09:45.0348432Z | Running benchmarks | 0.370 | 15968 |
| 2026-09-05T11:09:53.2006585Z | 2026-09-05T11:10:33.2141013Z | Running benchmarks | 0.667 | 16018 |
| 2026-09-05T11:10:42.8836342Z | 2026-09-05T11:10:43.1947439Z | Building bootstrap | 0.005 | 16077 |
| 2026-09-05T11:10:44.1540053Z | 2026-09-05T11:10:46.1170628Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.033 | 16103 |
| 2026-09-05T11:10:46.3175300Z | 2026-09-05T11:10:46.6148096Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.005 | 16426 |
| 2026-09-05T11:10:46.6158414Z | 2026-09-05T11:10:46.6847908Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.001 | 16483 |
| 2026-09-05T11:10:46.6852540Z | 2026-09-05T11:10:47.0247304Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.006 | 16491 |
| 2026-09-05T11:10:47.0251869Z | 2026-09-05T11:10:47.1522312Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.002 | 16563 |
| 2026-09-05T11:10:47.3636090Z | 2026-09-05T11:10:47.6721695Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-unknown-linux-gnu) | 0.005 | 16615 |
| 2026-09-05T11:10:47.6781635Z | 2026-09-05T11:13:52.9494610Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-unknown-linux-gnu) | 3.088 | 16657 |
| 2026-09-05T11:13:53.1450472Z | 2026-09-05T11:14:07.7939691Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.244 | 17214 |
| 2026-09-05T11:14:07.7945766Z | 2026-09-05T11:14:07.8627552Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.001 | 17270 |
| 2026-09-05T11:14:07.8632190Z | 2026-09-05T11:14:08.1561618Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.005 | 17278 |
| 2026-09-05T11:14:08.1572201Z | 2026-09-05T11:14:08.2760991Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.002 | 17350 |
| 2026-09-05T11:14:08.2776334Z | 2026-09-05T11:15:32.5727538Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, x86_64-unknown-linux-gnu) | 1.405 | 17405 |
| 2026-09-05T11:15:32.6651004Z | 2026-09-05T11:18:48.7111313Z | Building stage2 cargo (stage1 -> stage2, x86_64-unknown-linux-gnu) | 3.267 | 17572 |
| 2026-09-05T11:18:48.7117713Z | 2026-09-05T11:20:33.1185373Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-unknown-linux-gnu) | 1.740 | 18280 |
| 2026-09-05T11:20:33.1190878Z | 2026-09-05T11:20:33.2353819Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.002 | 18450 |
| 2026-09-05T11:20:33.8248437Z | 2026-09-05T11:20:33.8771242Z | Building bootstrap | 0.001 | 18609 |
| 2026-09-05T11:20:34.0459748Z | 2026-09-05T11:23:54.8240943Z | Building LLVM for x86_64-unknown-linux-gnu | 3.346 | 18620 |
| 2026-09-05T11:23:54.8342413Z | 2026-09-05T11:24:01.8057057Z | Building LLD for x86_64-unknown-linux-gnu | 0.116 | 26213 |
| 2026-09-05T11:24:01.8061345Z | 2026-09-05T11:24:01.8691398Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.001 | 26489 |
| 2026-09-05T11:24:01.8695879Z | 2026-09-05T11:24:01.9578632Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.001 | 26497 |
| 2026-09-05T11:24:01.9582825Z | 2026-09-05T11:24:02.0395495Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.001 | 26569 |
| 2026-09-05T11:24:02.1488983Z | 2026-09-05T11:24:02.2111696Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.001 | 26636 |
| 2026-09-05T11:24:02.2115722Z | 2026-09-05T11:24:02.2854367Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.001 | 26644 |
| 2026-09-05T11:24:02.2858248Z | 2026-09-05T11:24:02.3575216Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.001 | 26716 |
| 2026-09-05T11:24:02.3689895Z | 2026-09-05T11:27:01.2188577Z | Running benchmarks | 2.981 | 26770 |
| 2026-09-05T11:27:35.3863978Z | 2026-09-05T11:27:35.7163508Z | Building bootstrap | 0.005 | 26874 |
| 2026-09-05T11:27:36.0956275Z | 2026-09-05T11:37:50.7484204Z | Building LLVM for x86_64-unknown-linux-gnu | 10.244 | 26885 |
| 2026-09-05T11:37:51.2513478Z | 2026-09-05T11:37:58.2777240Z | Building LLD for x86_64-unknown-linux-gnu | 0.117 | 34478 |
| 2026-09-05T11:37:58.2781729Z | 2026-09-05T11:37:58.4643347Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.003 | 34754 |
| 2026-09-05T11:37:58.4647094Z | 2026-09-05T11:37:58.8860597Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.007 | 34762 |
| 2026-09-05T11:37:58.8865179Z | 2026-09-05T11:37:59.0566124Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.003 | 34834 |
| 2026-09-05T11:37:59.4307358Z | 2026-09-05T11:37:59.4987260Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.001 | 34901 |
| 2026-09-05T11:37:59.4991433Z | 2026-09-05T11:37:59.8394260Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.006 | 34909 |
| 2026-09-05T11:37:59.8398515Z | 2026-09-05T11:37:59.9858731Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.002 | 34981 |
| 2026-09-05T11:38:47.9387203Z | 2026-09-05T11:41:31.8041671Z | Running benchmarks | 2.731 | 35120 |
| 2026-09-05T11:41:31.8048090Z | 2026-09-05T11:42:31.3229565Z | Merging BOLT profiles | 0.992 | 35167 |
| 2026-09-05T11:43:16.5824665Z | 2026-09-05T11:48:29.6692504Z | Running benchmarks | 5.218 | 35223 |
| 2026-09-05T11:48:29.6702686Z | 2026-09-05T11:51:28.4214019Z | Merging BOLT profiles | 2.979 | 35289 |
| 2026-09-05T11:53:27.9926249Z | 2026-09-05T11:53:28.2170489Z | Building bootstrap | 0.004 | 35446 |
| 2026-09-05T11:53:28.9716426Z | 2026-09-05T11:53:29.1007803Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.002 | 35481 |
| 2026-09-05T11:53:29.1011931Z | 2026-09-05T11:53:29.3324821Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.004 | 35489 |
| 2026-09-05T11:53:29.3329392Z | 2026-09-05T11:53:29.4556828Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.002 | 35561 |
| 2026-09-05T11:53:29.5848731Z | 2026-09-05T11:53:41.4222290Z | Building stage1 unstable-book-gen (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.197 | 35621 |
| 2026-09-05T11:53:43.8783819Z | 2026-09-05T11:54:00.5937116Z | Building stage1 rustbook (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.279 | 35853 |
| 2026-09-05T11:54:03.6594925Z | 2026-09-05T11:54:03.6618843Z | Documenting stage2 book redirect pages (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 36280 |
| 2026-09-05T11:54:03.6619146Z | 2026-09-05T11:55:08.0236180Z | Building stage1 rustdoc-tool-binary (stage0 -> stage1, x86_64-unknown-linux-gnu) | 1.073 | 36284 |
| 2026-09-05T11:55:08.0236531Z | 2026-09-05T11:55:08.5955161Z | Documenting stage2 book redirect pages (stage1 -> stage2, x86_64-unknown-linux-gnu) (continued) | 0.010 | 36469 |
| 2026-09-05T11:55:08.5956736Z | 2026-09-05T11:55:08.7826708Z | Documenting stage2 standalone (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.003 | 36475 |
| 2026-09-05T11:55:08.7830541Z | 2026-09-05T11:55:25.4894811Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage1 -> stage1, x86_64-unknown-linux-gnu) | 0.278 | 36479 |
| 2026-09-05T11:55:25.4912313Z | 2026-09-05T11:56:11.6913752Z | Documenting stage2 compiler{rustc-main, rustc_abi, rustc_arena, rustc_ast, rustc_ast_ir, rustc_ast_lowering, rustc_ast_passes, rustc_ast_pretty, rustc_attr_ir, rustc_attr_parsing, rustc_baked_icu_data, rustc_borrowck, rustc_builtin_macros, rustc_codegen_llvm, rustc_codegen_ssa, rustc_const_eval, rustc_crate_store, rustc_data_structures, rustc_driver, rustc_driver_impl, rustc_error_codes, rustc_error_messages, rustc_errors, rustc_expand, rustc_feature, rustc_fs_util, rustc_graphviz, rustc_hashes, rustc_hir, rustc_hir_analysis, rustc_hir_id, rustc_hir_pretty, rustc_hir_typeck, rustc_incremental, rustc_index, rustc_index_macros, rustc_infer, rustc_interface, rustc_lexer, rustc_lint, rustc_lint_defs, rustc_llvm, rustc_log, rustc_macros, rustc_metadata, rustc_middle, rustc_mir_build, rustc_mir_dataflow, rustc_mir_transform, rustc_monomorphize, rustc_next_trait_solver, rustc_parse, rustc_parse_format, rustc_passes, rustc_pattern_analysis, rustc_privacy, rustc_proc_macro, rustc_public, rustc_public_bridge, rustc_query_impl, rustc_resolve, rustc_sanitizers, rustc_serialize, rustc_session, rustc_span, rustc_structures, rustc_symbol_mangling, rustc_target, rustc_thread_pool, rustc_trait_selection, rustc_traits, rustc_transmute, rustc_ty_utils, rustc_ty_walk, rustc_type_ir, rustc_type_ir_macros, rustc_windows_rc} (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.770 | 36548 |
| 2026-09-05T11:56:11.8946313Z | 2026-09-05T11:56:11.9611928Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.001 | 37224 |
| 2026-09-05T11:56:11.9615833Z | 2026-09-05T11:56:12.1738164Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.004 | 37232 |
| 2026-09-05T11:56:12.1743286Z | 2026-09-05T11:56:12.2849729Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.002 | 37304 |
| 2026-09-05T11:56:12.2860549Z | 2026-09-05T11:56:23.1102622Z | Documenting stage2 rustdoc (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.180 | 37351 |
| 2026-09-05T11:56:23.1109993Z | 2026-09-05T11:56:31.0349006Z | Documenting stage2 rustfmt (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.132 | 37540 |
| 2026-09-05T11:56:31.0354361Z | 2026-09-05T11:56:43.6629160Z | Building stage2 error_index_generator (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.210 | 37725 |
| 2026-09-05T11:57:05.0162964Z | 2026-09-05T11:57:07.5685650Z | Building stage1 lint-docs (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.043 | 38062 |
| 2026-09-05T11:57:07.5726638Z | 2026-09-05T11:57:17.2364279Z | Running stage2 lint-docs (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.161 | 38096 |
| 2026-09-05T11:57:17.6010944Z | 2026-09-05T11:58:01.8230892Z | Documenting stage2 cargo (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.737 | 38109 |
| 2026-09-05T11:58:02.1700910Z | 2026-09-05T11:58:05.1907360Z | Documenting stage2 clippy (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.050 | 38937 |
| 2026-09-05T11:58:05.2952859Z | 2026-09-05T11:58:05.2969025Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.000 | 38980 |
| 2026-09-05T11:58:05.2969292Z | 2026-09-05T11:58:22.1067860Z | Documenting stage2 miri (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.280 | 38983 |
| 2026-09-05T11:58:22.1068242Z | 2026-09-05T11:58:22.1071460Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, x86_64-unknown-linux-gnu) (continued) | 0.000 | 39151 |
| 2026-09-05T11:58:22.1071832Z | 2026-09-05T11:58:28.5232536Z | Documenting stage2 tidy (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.107 | 39155 |
| 2026-09-05T11:58:28.5232904Z | 2026-09-05T11:58:28.5236091Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, x86_64-unknown-linux-gnu) (continued) | 0.000 | 39372 |
| 2026-09-05T11:58:28.5236388Z | 2026-09-05T11:58:38.4259658Z | Documenting stage2 bootstrap (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.165 | 39376 |
| 2026-09-05T11:58:38.4260026Z | 2026-09-05T11:58:38.4263608Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, x86_64-unknown-linux-gnu) (continued) | 0.000 | 39541 |
| 2026-09-05T11:58:38.4263898Z | 2026-09-05T11:58:39.2663980Z | Documenting stage2 buildhelper (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.014 | 39545 |
| 2026-09-05T11:58:39.2664362Z | 2026-09-05T11:58:39.2667253Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, x86_64-unknown-linux-gnu) (continued) | 0.000 | 39552 |
| 2026-09-05T11:58:39.2667535Z | 2026-09-05T11:58:44.0009837Z | Documenting stage2 compiletest (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.079 | 39556 |
| 2026-09-05T11:58:44.0010280Z | 2026-09-05T11:58:44.0013139Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, x86_64-unknown-linux-gnu) (continued) | 0.000 | 39698 |
| 2026-09-05T11:58:44.0013437Z | 2026-09-05T11:58:48.7778803Z | Documenting stage2 runmakesupport (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.080 | 39702 |
| 2026-09-05T11:58:48.7779213Z | 2026-09-05T11:58:51.8868821Z | Documenting stage2 compiler-with-tools (stage1 -> stage2, x86_64-unknown-linux-gnu) (continued) | 0.052 | 39785 |
| 2026-09-05T11:58:52.1526301Z | 2026-09-05T11:58:52.1944649Z | Documenting stage2 releases (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.001 | 39818 |
| 2026-09-05T11:58:52.7050229Z | 2026-09-05T11:59:03.4957376Z | Building stage1 rust-installer (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.180 | 39823 |
| 2026-09-05T11:59:53.1087608Z | 2026-09-05T12:00:00.1936087Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage1 -> stage1, x86_64-unknown-linux-gnu) | 0.118 | 39911 |
| 2026-09-05T12:00:04.4069195Z | 2026-09-05T12:00:33.5890926Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.486 | 39961 |
| 2026-09-05T12:00:33.6387082Z | 2026-09-05T12:00:51.8570638Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.304 | 40071 |
| 2026-09-05T12:00:51.8773926Z | 2026-09-05T12:01:01.2769387Z | Vendoring sources to "/checkout" | 0.157 | 40255 |
| 2026-09-05T12:01:01.2770538Z | 2026-09-05T12:01:01.2773752Z | generate-copyright | 0.000 | 42413 |
| 2026-09-05T12:01:01.2774052Z | 2026-09-05T12:01:16.0765047Z | Building stage1 generate-copyright (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.247 | 42417 |
| 2026-09-05T12:01:16.0765305Z | 2026-09-05T12:01:17.2790083Z | generate-copyright (continued) | 0.020 | 42548 |
| 2026-09-05T12:02:27.1292331Z | 2026-09-05T12:02:27.1948434Z | Vendoring sources to "/checkout/obj/build/tmp/tarball/rust-src/image/lib/rustlib/src/rust" | 0.001 | 46938 |
| 2026-09-05T12:02:32.6388287Z | 2026-09-05T12:02:33.6765586Z | Building stage2 cargo (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.017 | 46980 |
| 2026-09-05T12:02:40.9178703Z | 2026-09-05T12:04:50.4353522Z | Building stage2 rust-analyzer (stage1 -> stage2, x86_64-unknown-linux-gnu) | 2.159 | 47379 |
| 2026-09-05T12:04:57.5562414Z | 2026-09-05T12:05:24.0465591Z | Building stage2 rustfmt (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.442 | 47872 |
| 2026-09-05T12:05:24.0471410Z | 2026-09-05T12:05:24.1500613Z | Building stage2 cargo-fmt (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.002 | 48047 |
| 2026-09-05T12:05:25.7255061Z | 2026-09-05T12:06:01.3173533Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.593 | 48158 |
| 2026-09-05T12:06:01.3178725Z | 2026-09-05T12:06:01.4196494Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.002 | 48262 |
| 2026-09-05T12:06:05.0894185Z | 2026-09-05T12:06:54.4002670Z | Building stage2 miri (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.822 | 48369 |
| 2026-09-05T12:06:54.4008751Z | 2026-09-05T12:07:00.4712584Z | Building stage2 cargo-miri (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.101 | 48611 |
| 2026-09-05T12:07:48.9289477Z | 2026-09-05T12:08:00.1405861Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage2 -> stage2, x86_64-unknown-linux-gnu) | 0.187 | 48706 |
| 2026-09-05T12:10:57.1506654Z | 2026-09-05T12:11:05.8784475Z | Vendoring sources to "/checkout/obj/build/tmp/tarball/rustc/src/image" | 0.145 | 48783 |
| 2026-09-05T12:15:04.1760800Z | 2026-09-05T12:15:14.3513532Z | Vendoring sources to "/checkout/obj/build/tmp/tarball/rustc/src-gpl/image" | 0.170 | 50900 |
| 2026-09-05T12:18:13.5110073Z | 2026-09-05T12:18:31.2910259Z | Building stage2 build-manifest (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.296 | 52848 |
| 2026-09-05T12:18:58.1398325Z | 2026-09-05T12:19:21.4891653Z | Building stage2 codegen backend gcc (stage1 -> stage2, x86_64-unknown-linux-gnu) | 0.389 | 53737 |
| 2026-09-05T12:19:29.0370209Z | 2026-09-05T12:19:38.7277162Z | Building bootstrap | 0.162 | 53969 |
| 2026-09-05T12:19:39.2163022Z | 2026-09-05T12:19:47.1793785Z | Building stage1 compiletest (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.133 | 54036 |
| 2026-09-05T12:19:47.1840280Z | 2026-09-05T12:19:49.4195381Z | Testing stage0 with compiletest suite=assembly-llvm mode=assembly (x86_64-unknown-linux-gnu) | 0.037 | 54115 |
| 2026-09-05T12:19:49.4209196Z | 2026-09-05T12:19:51.5487378Z | Testing stage0 with compiletest suite=codegen-llvm mode=codegen (x86_64-unknown-linux-gnu) | 0.035 | 54896 |
| 2026-09-05T12:19:51.5501195Z | 2026-09-05T12:19:51.7034087Z | Testing stage0 with compiletest suite=codegen-units mode=codegen-units (x86_64-unknown-linux-gnu) | 0.003 | 56128 |
| 2026-09-05T12:19:51.7047232Z | 2026-09-05T12:19:51.7606442Z | Building test helpers for x86_64-unknown-linux-gnu | 0.001 | 56181 |
| 2026-09-05T12:19:51.7607681Z | 2026-09-05T12:19:55.7836782Z | Testing stage0 with compiletest suite=incremental mode=incremental (x86_64-unknown-linux-gnu) | 0.067 | 56183 |
| 2026-09-05T12:19:55.7850672Z | 2026-09-05T12:19:56.9537397Z | Testing stage0 with compiletest suite=mir-opt mode=mir-opt (x86_64-unknown-linux-gnu) | 0.019 | 56370 |
| 2026-09-05T12:19:56.9550810Z | 2026-09-05T12:19:57.1974233Z | Testing stage0 with compiletest suite=pretty mode=pretty (x86_64-unknown-linux-gnu) | 0.004 | 56787 |
| 2026-09-05T12:19:57.1988854Z | 2026-09-05T12:20:02.4773080Z | Building stage1 run_make_support (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.088 | 56908 |
| 2026-09-05T12:20:02.4776066Z | 2026-09-05T12:20:02.7206781Z | Testing stage0 with compiletest suite=run-make mode=run-make (x86_64-unknown-linux-gnu) | 0.004 | 56938 |
| 2026-09-05T12:20:02.7223521Z | 2026-09-05T12:21:06.1086991Z | Testing stage0 with compiletest suite=ui mode=ui (x86_64-unknown-linux-gnu) | 1.056 | 56947 |
| 2026-09-05T12:21:06.1103605Z | 2026-09-05T12:21:06.3756696Z | Testing stage0 with compiletest suite=crashes mode=crashes (x86_64-unknown-linux-gnu) | 0.004 | 79147 |
| 2026-09-05T12:21:06.3773514Z | 2026-09-05T12:21:14.0859550Z | Testing stage0 with compiletest suite=rustdoc-html mode=rustdoc-html (x86_64-unknown-linux-gnu) | 0.128 | 79356 |
| 2026-09-05T12:21:14.1491287Z | 2026-09-05T12:21:23.5062381Z | Building bootstrap | 0.156 | 80226 |
| 2026-09-05T12:21:23.9408450Z | 2026-09-05T12:24:37.3633957Z | Building GCC for x86_64-unknown-linux-gnu -> x86_64-unknown-linux-gnu | 3.224 | 80234 |
| 2026-09-05T12:24:37.3660542Z | 2026-09-05T12:24:46.2350234Z | Building stage1 rust-installer (stage0 -> stage1, x86_64-unknown-linux-gnu) | 0.148 | 81082 |
| 2026-09-05T12:25:02.4072858Z | 2026-09-05T12:25:02.4100510Z | sccache stats | 0.000 | 81198 |
| 2026-09-05T12:25:02.4100721Z | 2026-09-05T12:25:02.4673388Z | Clock drift check | 0.001 | 81250 |
| 2026-09-05T11:59:03.5000076Z | 2026-09-05T11:59:21.2720904Z | Dist rust-docs-nightly-x86_64-unknown-linux-gnu | 0.296 | 39902 |
| 2026-09-05T11:59:21.7664469Z | 2026-09-05T11:59:53.1082291Z | Dist rustc-docs-nightly-x86_64-unknown-linux-gnu | 0.522 | 39906 |
| 2026-09-05T12:00:00.1981321Z | 2026-09-05T12:00:04.4061250Z | Dist rust-docs-json-nightly-x86_64-unknown-linux-gnu | 0.070 | 39953 |
| 2026-09-05T12:01:17.2905777Z | 2026-09-05T12:01:41.3964042Z | Dist rustc-nightly-x86_64-unknown-linux-gnu | 0.402 | 46917 |
| 2026-09-05T12:01:41.4032329Z | 2026-09-05T12:01:43.7048304Z | Dist rustc-codegen-cranelift-nightly-x86_64-unknown-linux-gnu | 0.038 | 46921 |
| 2026-09-05T12:01:43.7115543Z | 2026-09-05T12:01:51.8410828Z | Dist rust-std-nightly-x86_64-unknown-linux-gnu | 0.135 | 46925 |
| 2026-09-05T12:01:51.9656793Z | 2026-09-05T12:02:26.4209618Z | Dist rustc-dev-nightly-x86_64-unknown-linux-gnu | 0.574 | 46929 |
| 2026-09-05T12:02:26.4256748Z | 2026-09-05T12:02:26.4430163Z | Dist rust-analysis-nightly-x86_64-unknown-linux-gnu | 0.000 | 46933 |
| 2026-09-05T12:02:27.1993747Z | 2026-09-05T12:02:32.6384166Z | Dist rust-src-nightly | 0.091 | 46974 |
| 2026-09-05T12:02:33.6860263Z | 2026-09-05T12:02:40.9169754Z | Dist cargo-nightly-x86_64-unknown-linux-gnu | 0.121 | 47373 |
| 2026-09-05T12:04:50.4419717Z | 2026-09-05T12:04:57.5557466Z | Dist rust-analyzer-nightly-x86_64-unknown-linux-gnu | 0.119 | 47866 |
| 2026-09-05T12:05:24.1566050Z | 2026-09-05T12:05:25.7250061Z | Dist rustfmt-nightly-x86_64-unknown-linux-gnu | 0.026 | 48152 |
| 2026-09-05T12:06:01.4262175Z | 2026-09-05T12:06:05.0888660Z | Dist clippy-nightly-x86_64-unknown-linux-gnu | 0.061 | 48363 |
| 2026-09-05T12:07:00.4778854Z | 2026-09-05T12:07:02.9790445Z | Dist miri-nightly-x86_64-unknown-linux-gnu | 0.042 | 48685 |
| 2026-09-05T12:07:02.9856307Z | 2026-09-05T12:07:16.1664526Z | Dist llvm-tools-nightly-x86_64-unknown-linux-gnu | 0.220 | 48689 |
| 2026-09-05T12:07:16.1717166Z | 2026-09-05T12:07:16.5572353Z | Dist llvm-bitcode-linker-nightly-x86_64-unknown-linux-gnu | 0.006 | 48693 |
| 2026-09-05T12:07:17.6314767Z | 2026-09-05T12:07:48.9281825Z | Dist rust-dev-nightly-x86_64-unknown-linux-gnu | 0.522 | 48699 |
| 2026-09-05T12:08:00.1499162Z | 2026-09-05T12:08:04.2926939Z | Dist rust-docs-json-nightly-x86_64-unknown-linux-gnu | 0.069 | 48775 |
| 2026-09-05T12:08:04.2974498Z | 2026-09-05T12:09:22.9383435Z | Dist rust-nightly-x86_64-unknown-linux-gnu | 1.311 | 48778 |
| 2026-09-05T12:11:06.6735035Z | 2026-09-05T12:13:03.3697689Z | Dist rustc-nightly-src | 1.945 | 50895 |
| 2026-09-05T12:15:16.2777290Z | 2026-09-05T12:17:49.0569395Z | Dist rustc-nightly-src-gpl | 2.546 | 52838 |
| 2026-09-05T12:17:50.5893122Z | 2026-09-05T12:18:13.5104596Z | Dist reproducible-artifacts-nightly-x86_64-unknown-linux-gnu | 0.382 | 52842 |
| 2026-09-05T12:18:31.2956986Z | 2026-09-05T12:18:31.6689503Z | Dist build-manifest-nightly-x86_64-unknown-linux-gnu | 0.006 | 52970 |
| 2026-09-05T12:18:31.6742540Z | 2026-09-05T12:18:37.3720002Z | Dist bootstrap-nightly-x86_64-unknown-linux-gnu | 0.095 | 52974 |
| 2026-09-05T12:18:43.0483236Z | 2026-09-05T12:18:44.9436648Z | Dist enzyme-nightly-x86_64-unknown-linux-gnu | 0.032 | 53117 |
| 2026-09-05T12:18:56.4273073Z | 2026-09-05T12:18:58.1385655Z | Dist offload-nightly-x86_64-unknown-linux-gnu | 0.029 | 53732 |
| 2026-09-05T12:19:21.4935711Z | 2026-09-05T12:19:22.1412045Z | Dist rustc-codegen-gcc-nightly-x86_64-unknown-linux-gnu | 0.011 | 53774 |
| 2026-09-05T12:24:46.2370245Z | 2026-09-05T12:24:54.3237567Z | Dist gcc-dev-nightly-x86_64-unknown-linux-gnu | 0.135 | 81183 |
| 2026-09-05T12:24:54.3265224Z | 2026-09-05T12:25:02.3867277Z | Dist gcc-x86_64-unknown-linux-gnu-nightly-x86_64-unknown-linux-gnu | 0.134 | 81187 |

</details>

| opt-dist timer (nested) | Minutes |
|---|---:|
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Build PGO instrumented rustc and LLVM | 20.992 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather rustc profiles | 4.749 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather rustdoc profiles | 0.506 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather clippy profiles | 0.824 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Build PGO optimized rustc | 9.843 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) | 36.913 |
| Stage 2 (LLVM PGO) > Build PGO instrumented LLVM | 3.477 |
| Stage 2 (LLVM PGO) > Gather profiles | 3.544 |
| Stage 2 (LLVM PGO) | 7.034 |
| Stage 3 (BOLT) > Build PGO optimized LLVM | 10.412 |
| Stage 3 (BOLT) > Instrument & gather profiles > Gather profiles | 3.730 |
| Stage 3 (BOLT) > Instrument & gather profiles | 4.547 |
| Stage 3 (BOLT) > Instrument & gather profiles > Gather profiles | 8.206 |
| Stage 3 (BOLT) > Instrument & gather profiles | 8.949 |
| Stage 3 (BOLT) > Optimize LLVM and rustc with BOLT | 1.968 |
| Stage 3 (BOLT) | 25.877 |
| Stage 5 (final build) | 25.905 |
| Run tests | 1.866 |

## [auto - dist-x86_64-msvc: 101293559559](https://github.com/rust-lang/rust/actions/runs/33961251131/job/101293559559)

Run 33961251131; raw SHA256 `6db512c1833ce5a05f71537389059979ded4fa35da5fa5393de1ee3520e8ccee`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 3.512 |
| Build support | 3.809 |
| LLVM/LLD | 18.664 |
| Compiler | 20.659 |
| Tools | 47.676 |
| Libraries | 0.773 |
| Tests | 28.687 |
| Docs | 3.984 |
| Packaging | 14.418 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-05T10:47:51.6263767Z | 2026-09-05T10:47:51.6291624Z | Run set +e | 0.000 | 1860 |
| 2026-09-05T10:47:53.5024318Z | 2026-09-05T10:47:53.6083362Z | Clock drift check | 0.002 | 1909 |
| 2026-09-05T10:47:55.1074432Z | 2026-09-05T10:47:55.1092937Z | Configure the build | 0.000 | 1915 |
| 2026-09-05T10:48:05.8506657Z | 2026-09-05T10:48:39.7451739Z | Building bootstrap | 0.565 | 1961 |
| 2026-09-05T10:48:41.7168904Z | 2026-09-05T10:48:41.7224646Z | Building LLVM for x86_64-pc-windows-msvc | 0.000 | 2141 |
| 2026-09-05T10:48:41.7246698Z | 2026-09-05T10:48:41.7254190Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2143 |
| 2026-09-05T10:48:41.7258273Z | 2026-09-05T10:48:41.7258902Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2146 |
| 2026-09-05T10:48:41.7264421Z | 2026-09-05T10:48:41.7269557Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2148 |
| 2026-09-05T10:48:41.7277590Z | 2026-09-05T10:48:41.7278489Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2150 |
| 2026-09-05T10:48:41.7281337Z | 2026-09-05T10:48:41.7282757Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2152 |
| 2026-09-05T10:48:41.7292084Z | 2026-09-05T10:48:41.7295702Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-pc-windows-msvc) | 0.000 | 2154 |
| 2026-09-05T10:48:41.7389366Z | 2026-09-05T10:48:41.7390213Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2156 |
| 2026-09-05T10:48:41.7391668Z | 2026-09-05T10:48:41.7392427Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2159 |
| 2026-09-05T10:48:41.7393055Z | 2026-09-05T10:48:41.7393536Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2161 |
| 2026-09-05T10:48:41.7394281Z | 2026-09-05T10:48:41.7394826Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2163 |
| 2026-09-05T10:48:41.7395641Z | 2026-09-05T10:48:41.7396157Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2165 |
| 2026-09-05T10:48:41.7396769Z | 2026-09-05T10:48:41.7397178Z | Building stage2 cargo (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2168 |
| 2026-09-05T10:48:41.7397543Z | 2026-09-05T10:48:41.7397953Z | Building stage2 rust-analyzer (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2170 |
| 2026-09-05T10:48:41.7398364Z | 2026-09-05T10:48:41.7398825Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2172 |
| 2026-09-05T10:48:41.7399200Z | 2026-09-05T10:48:41.7399639Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2174 |
| 2026-09-05T10:48:41.7400005Z | 2026-09-05T10:48:41.7400403Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2176 |
| 2026-09-05T10:48:41.7400755Z | 2026-09-05T10:48:41.7401165Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2178 |
| 2026-09-05T10:48:41.7401505Z | 2026-09-05T10:48:41.7401894Z | Building stage2 rustfmt (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2180 |
| 2026-09-05T10:48:41.7402267Z | 2026-09-05T10:48:41.7402668Z | Building stage2 cargo-fmt (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2182 |
| 2026-09-05T10:48:41.7402994Z | 2026-09-05T10:48:41.7403380Z | Building stage2 miri (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2184 |
| 2026-09-05T10:48:41.7403733Z | 2026-09-05T10:48:41.7404154Z | Building stage2 cargo-miri (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 2186 |
| 2026-09-05T10:48:41.7557682Z | 2026-09-05T10:48:41.8212708Z | Display CPU and Memory information | 0.001 | 2189 |
| 2026-09-05T10:48:41.9870613Z | 2026-09-05T10:48:42.0958327Z | Building bootstrap | 0.002 | 2409 |
| 2026-09-05T10:48:42.6919513Z | 2026-09-05T10:49:17.0709398Z | Building stage1 opt-dist (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.573 | 2422 |
| 2026-09-05T10:49:17.0986295Z | 2026-09-05T10:49:17.1058266Z | Environment values | 0.000 | 2677 |
| 2026-09-05T10:49:17.1058590Z | 2026-09-05T10:49:17.1113621Z | Printing bootstrap.toml | 0.000 | 2862 |
| 2026-09-05T10:49:17.1114476Z | 2026-09-05T10:50:46.5567439Z | Building rustc-perf | 1.491 | 3055 |
| 2026-09-05T10:50:46.6459989Z | 2026-09-05T10:50:46.7571538Z | Building bootstrap | 0.002 | 3631 |
| 2026-09-05T10:50:47.3894195Z | 2026-09-05T10:56:22.1358830Z | Building LLVM for x86_64-pc-windows-msvc | 5.579 | 3642 |
| 2026-09-05T10:56:22.1961024Z | 2026-09-05T11:02:43.5769245Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-pc-windows-msvc) | 6.356 | 10834 |
| 2026-09-05T11:02:43.5849235Z | 2026-09-05T11:06:04.2107292Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-pc-windows-msvc) | 3.344 | 11555 |
| 2026-09-05T11:06:04.2124971Z | 2026-09-05T11:06:17.7997392Z | Building LLD for x86_64-pc-windows-msvc | 0.226 | 11674 |
| 2026-09-05T11:06:17.8005336Z | 2026-09-05T11:06:18.5176518Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.012 | 11913 |
| 2026-09-05T11:06:18.5368043Z | 2026-09-05T11:06:56.9579315Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.640 | 11922 |
| 2026-09-05T11:06:56.9601701Z | 2026-09-05T11:07:10.3353941Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.223 | 12064 |
| 2026-09-05T11:07:10.3398829Z | 2026-09-05T11:07:55.3982214Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-pc-windows-msvc) | 0.751 | 12145 |
| 2026-09-05T11:07:55.3993478Z | 2026-09-05T11:14:37.7991917Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-pc-windows-msvc) | 6.707 | 12204 |
| 2026-09-05T11:14:37.8029448Z | 2026-09-05T11:18:21.8474080Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-pc-windows-msvc) | 3.734 | 12808 |
| 2026-09-05T11:18:21.8497891Z | 2026-09-05T11:18:22.5856244Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.012 | 12902 |
| 2026-09-05T11:18:22.5914460Z | 2026-09-05T11:19:06.8202278Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.737 | 12911 |
| 2026-09-05T11:19:06.8230374Z | 2026-09-05T11:19:22.7758399Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.266 | 13040 |
| 2026-09-05T11:19:22.7972867Z | 2026-09-05T11:21:47.5480015Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, x86_64-pc-windows-msvc) | 2.413 | 13123 |
| 2026-09-05T11:21:47.5595933Z | 2026-09-05T11:28:27.6272329Z | Building stage2 cargo (stage1 -> stage2, x86_64-pc-windows-msvc) | 6.668 | 13331 |
| 2026-09-05T11:28:27.6290706Z | 2026-09-05T11:31:13.8387725Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-pc-windows-msvc) | 2.770 | 14212 |
| 2026-09-05T11:31:13.8413790Z | 2026-09-05T11:31:14.2294569Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.006 | 14403 |
| 2026-09-05T11:31:14.2523074Z | 2026-09-05T11:42:40.2154938Z | Running benchmarks | 11.433 | 14560 |
| 2026-09-05T11:43:20.9242754Z | 2026-09-05T11:44:53.4956777Z | Running benchmarks | 1.543 | 14633 |
| 2026-09-05T11:45:09.8540274Z | 2026-09-05T11:47:20.3641611Z | Running benchmarks | 2.175 | 14687 |
| 2026-09-05T11:47:39.3840899Z | 2026-09-05T11:47:39.6151330Z | Building bootstrap | 0.004 | 14743 |
| 2026-09-05T11:47:40.8071905Z | 2026-09-05T11:47:42.3966138Z | Building stage1 compiler artifacts (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.026 | 14769 |
| 2026-09-05T11:47:42.4046028Z | 2026-09-05T11:47:42.7357097Z | Building stage1 codegen backend cranelift (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.006 | 15098 |
| 2026-09-05T11:47:42.7378114Z | 2026-09-05T11:47:42.9923692Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.004 | 15155 |
| 2026-09-05T11:47:42.9977179Z | 2026-09-05T11:47:43.4638098Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.008 | 15163 |
| 2026-09-05T11:47:43.4661114Z | 2026-09-05T11:47:43.7762327Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.005 | 15235 |
| 2026-09-05T11:47:43.7806443Z | 2026-09-05T11:47:44.3692441Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-pc-windows-msvc) | 0.010 | 15289 |
| 2026-09-05T11:47:44.3699875Z | 2026-09-05T11:54:10.6875608Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-pc-windows-msvc) | 6.439 | 15323 |
| 2026-09-05T11:54:10.6905138Z | 2026-09-05T11:54:34.4117554Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.395 | 15894 |
| 2026-09-05T11:54:34.4137363Z | 2026-09-05T11:54:34.6812271Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.004 | 15950 |
| 2026-09-05T11:54:34.6864287Z | 2026-09-05T11:54:35.0510434Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.006 | 15958 |
| 2026-09-05T11:54:35.0533191Z | 2026-09-05T11:54:35.3680532Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.005 | 16030 |
| 2026-09-05T11:54:35.3904370Z | 2026-09-05T11:56:26.2250760Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, x86_64-pc-windows-msvc) | 1.847 | 16089 |
| 2026-09-05T11:56:26.2279851Z | 2026-09-05T12:01:34.8948696Z | Building stage2 cargo (stage1 -> stage2, x86_64-pc-windows-msvc) | 5.144 | 16257 |
| 2026-09-05T12:01:34.8967876Z | 2026-09-05T12:04:05.1468830Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-pc-windows-msvc) | 2.504 | 16964 |
| 2026-09-05T12:04:05.1492700Z | 2026-09-05T12:04:05.5167830Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.006 | 17142 |
| 2026-09-05T12:04:06.7821439Z | 2026-09-05T12:04:06.9078773Z | Building bootstrap | 0.002 | 17304 |
| 2026-09-05T12:04:07.6164704Z | 2026-09-05T12:11:07.2724700Z | Building LLVM for x86_64-pc-windows-msvc | 6.994 | 17315 |
| 2026-09-05T12:11:07.4519057Z | 2026-09-05T12:11:23.9428842Z | Building LLD for x86_64-pc-windows-msvc | 0.275 | 24521 |
| 2026-09-05T12:11:23.9441386Z | 2026-09-05T12:11:25.0150646Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.018 | 24760 |
| 2026-09-05T12:11:25.0207103Z | 2026-09-05T12:11:25.4467045Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.007 | 24768 |
| 2026-09-05T12:11:25.4487821Z | 2026-09-05T12:11:25.7801224Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.006 | 24840 |
| 2026-09-05T12:11:25.9985156Z | 2026-09-05T12:11:27.2173249Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.020 | 24909 |
| 2026-09-05T12:11:27.2228265Z | 2026-09-05T12:11:27.9074070Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.011 | 24917 |
| 2026-09-05T12:11:27.9098194Z | 2026-09-05T12:11:28.2366300Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.005 | 24989 |
| 2026-09-05T12:11:28.2821157Z | 2026-09-05T12:17:12.7114671Z | Running benchmarks | 5.740 | 25090 |
| 2026-09-05T12:17:20.8481927Z | 2026-09-05T12:17:21.0463032Z | Building bootstrap | 0.003 | 25149 |
| 2026-09-05T12:17:22.2758603Z | 2026-09-05T12:22:44.0154068Z | Building LLVM for x86_64-pc-windows-msvc | 5.362 | 25161 |
| 2026-09-05T12:22:44.1092150Z | 2026-09-05T12:22:57.7317815Z | Building LLD for x86_64-pc-windows-msvc | 0.227 | 32362 |
| 2026-09-05T12:22:57.7324611Z | 2026-09-05T12:22:58.2892242Z | Building stage1 lld-wrapper (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.009 | 32601 |
| 2026-09-05T12:22:58.2944697Z | 2026-09-05T12:22:58.5971159Z | Building stage1 wasm-component-ld (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.005 | 32609 |
| 2026-09-05T12:22:58.5990097Z | 2026-09-05T12:22:58.8836725Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.005 | 32681 |
| 2026-09-05T12:22:58.8878792Z | 2026-09-05T12:22:59.6426180Z | Building stage1 library artifacts (stage1 -> stage1, x86_64-pc-windows-msvc) | 0.013 | 32734 |
| 2026-09-05T12:22:59.6441730Z | 2026-09-05T12:23:48.5821152Z | Building stage1 unstable-book-gen (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.816 | 32773 |
| 2026-09-05T12:23:51.1609087Z | 2026-09-05T12:24:33.8931042Z | Building stage1 rustbook (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.712 | 33008 |
| 2026-09-05T12:24:39.2007541Z | 2026-09-05T12:24:39.2161479Z | Documenting stage2 book redirect pages (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.000 | 33437 |
| 2026-09-05T12:24:39.2162068Z | 2026-09-05T12:26:57.9732715Z | Building stage1 rustdoc-tool-binary (stage0 -> stage1, x86_64-pc-windows-msvc) | 2.313 | 33441 |
| 2026-09-05T12:26:57.9733716Z | 2026-09-05T12:26:59.9013744Z | Documenting stage2 book redirect pages (stage1 -> stage2, x86_64-pc-windows-msvc) (continued) | 0.032 | 33627 |
| 2026-09-05T12:26:59.9021273Z | 2026-09-05T12:27:00.5901904Z | Documenting stage2 standalone (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.011 | 33633 |
| 2026-09-05T12:27:00.5920492Z | 2026-09-05T12:27:56.2183445Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage1 -> stage1, x86_64-pc-windows-msvc) | 0.927 | 33637 |
| 2026-09-05T12:27:56.2263221Z | 2026-09-05T12:29:04.0745711Z | Building stage2 compiler artifacts (stage1 -> stage2, x86_64-pc-windows-msvc) | 1.131 | 33697 |
| 2026-09-05T12:29:04.0775329Z | 2026-09-05T12:29:27.5243361Z | Building stage2 codegen backend cranelift (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.391 | 34032 |
| 2026-09-05T12:29:27.5262670Z | 2026-09-05T12:29:27.7880468Z | Building stage2 lld-wrapper (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.004 | 34088 |
| 2026-09-05T12:29:27.7937912Z | 2026-09-05T12:29:28.1007219Z | Building stage2 wasm-component-ld (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.005 | 34096 |
| 2026-09-05T12:29:28.1028942Z | 2026-09-05T12:29:28.3933574Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.005 | 34168 |
| 2026-09-05T12:29:28.3965558Z | 2026-09-05T12:30:01.7648456Z | Building stage2 error_index_generator (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.556 | 34222 |
| 2026-09-05T12:30:14.2146915Z | 2026-09-05T12:30:18.7406955Z | Building stage1 lint-docs (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.075 | 34555 |
| 2026-09-05T12:30:18.7685199Z | 2026-09-05T12:30:37.8688163Z | Running stage2 lint-docs (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.318 | 34586 |
| 2026-09-05T12:30:40.0969570Z | 2026-09-05T12:30:40.2498623Z | Documenting stage2 releases (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.003 | 34644 |
| 2026-09-05T12:30:56.3273222Z | 2026-09-05T12:31:17.7101228Z | Building stage1 rust-installer (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.356 | 34649 |
| 2026-09-05T12:32:20.7490540Z | 2026-09-05T12:32:33.0975116Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage1 -> stage1, x86_64-pc-windows-msvc) | 0.206 | 34734 |
| 2026-09-05T12:32:40.0517584Z | 2026-09-05T12:34:23.8119130Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, x86_64-pc-windows-msvc) | 1.729 | 34776 |
| 2026-09-05T12:34:23.8162850Z | 2026-09-05T12:35:06.4477378Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.711 | 34887 |
| 2026-09-05T12:35:06.4942228Z | 2026-09-05T12:36:19.8939176Z | Vendoring sources to "C:\\a\\rust\\rust" | 1.223 | 35078 |
| 2026-09-05T12:36:19.8943095Z | 2026-09-05T12:36:19.8951416Z | generate-copyright | 0.000 | 37253 |
| 2026-09-05T12:36:19.8951968Z | 2026-09-05T12:36:44.5036848Z | Building stage1 generate-copyright (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.410 | 37257 |
| 2026-09-05T12:36:44.5037304Z | 2026-09-05T12:36:47.7001999Z | generate-copyright (continued) | 0.053 | 37388 |
| 2026-09-05T12:38:49.3625955Z | 2026-09-05T12:38:50.0372874Z | Vendoring sources to "C:\\a\\rust\\rust\\build\\tmp\\tarball\\rust-src\\image\\lib/rustlib/src/rust" | 0.011 | 41778 |
| 2026-09-05T12:39:00.5852077Z | 2026-09-05T12:39:01.4848251Z | Building stage2 cargo (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.015 | 41820 |
| 2026-09-05T12:39:10.5032397Z | 2026-09-05T12:43:44.1635560Z | Building stage2 rust-analyzer (stage1 -> stage2, x86_64-pc-windows-msvc) | 4.561 | 42215 |
| 2026-09-05T12:43:53.9534578Z | 2026-09-05T12:44:52.7488231Z | Building stage2 rustfmt (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.980 | 42718 |
| 2026-09-05T12:44:52.7509949Z | 2026-09-05T12:44:53.1342675Z | Building stage2 cargo-fmt (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.006 | 42902 |
| 2026-09-05T12:44:57.4633355Z | 2026-09-05T12:47:26.5682460Z | Building stage2 clippy-driver (stage1 -> stage2, x86_64-pc-windows-msvc) | 2.485 | 43016 |
| 2026-09-05T12:47:26.5760421Z | 2026-09-05T12:47:26.9714078Z | Building stage2 cargo-clippy (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.007 | 43127 |
| 2026-09-05T12:47:33.6648666Z | 2026-09-05T12:48:53.4536665Z | Building stage2 miri (stage1 -> stage2, x86_64-pc-windows-msvc) | 1.330 | 43238 |
| 2026-09-05T12:48:53.4560621Z | 2026-09-05T12:49:04.7546603Z | Building stage2 cargo-miri (stage1 -> stage2, x86_64-pc-windows-msvc) | 0.188 | 43440 |
| 2026-09-05T12:53:46.7802788Z | 2026-09-05T12:54:06.3954752Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage2 -> stage2, x86_64-pc-windows-msvc) | 0.327 | 43538 |
| 2026-09-05T13:00:57.9029838Z | 2026-09-05T13:01:24.7686921Z | Building bootstrap | 0.448 | 43786 |
| 2026-09-05T13:01:28.1118340Z | 2026-09-05T13:01:57.9802890Z | Building stage1 compiletest (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.498 | 43869 |
| 2026-09-05T13:01:58.0003948Z | 2026-09-05T13:02:12.7716871Z | Testing stage0 with compiletest suite=assembly-llvm mode=assembly (x86_64-pc-windows-msvc) | 0.246 | 43959 |
| 2026-09-05T13:02:12.7794365Z | 2026-09-05T13:02:27.7260066Z | Testing stage0 with compiletest suite=codegen-llvm mode=codegen (x86_64-pc-windows-msvc) | 0.249 | 44740 |
| 2026-09-05T13:02:27.7337387Z | 2026-09-05T13:02:28.6439824Z | Testing stage0 with compiletest suite=codegen-units mode=codegen-units (x86_64-pc-windows-msvc) | 0.015 | 45972 |
| 2026-09-05T13:02:28.6514580Z | 2026-09-05T13:02:28.7203440Z | Building test helpers for x86_64-pc-windows-msvc | 0.001 | 46025 |
| 2026-09-05T13:02:28.7206704Z | 2026-09-05T13:02:41.0359527Z | Testing stage0 with compiletest suite=incremental mode=incremental (x86_64-pc-windows-msvc) | 0.205 | 46028 |
| 2026-09-05T13:02:41.0436863Z | 2026-09-05T13:02:51.6796888Z | Testing stage0 with compiletest suite=mir-opt mode=mir-opt (x86_64-pc-windows-msvc) | 0.177 | 46215 |
| 2026-09-05T13:02:51.6880865Z | 2026-09-05T13:02:53.0998305Z | Testing stage0 with compiletest suite=pretty mode=pretty (x86_64-pc-windows-msvc) | 0.024 | 46632 |
| 2026-09-05T13:02:53.1077295Z | 2026-09-05T13:03:08.8008315Z | Building stage1 run_make_support (stage0 -> stage1, x86_64-pc-windows-msvc) | 0.262 | 46753 |
| 2026-09-05T13:03:08.8012712Z | 2026-09-05T13:03:09.0180733Z | Testing stage0 with compiletest suite=run-make mode=run-make (x86_64-pc-windows-msvc) | 0.004 | 46786 |
| 2026-09-05T13:03:09.0283441Z | 2026-09-05T13:09:15.9801698Z | Testing stage0 with compiletest suite=ui mode=ui (x86_64-pc-windows-msvc) | 6.116 | 46795 |
| 2026-09-05T13:09:15.9909869Z | 2026-09-05T13:09:17.7885825Z | Testing stage0 with compiletest suite=crashes mode=crashes (x86_64-pc-windows-msvc) | 0.030 | 68995 |
| 2026-09-05T13:09:17.7984367Z | 2026-09-05T13:10:01.6126792Z | Testing stage0 with compiletest suite=rustdoc-html mode=rustdoc-html (x86_64-pc-windows-msvc) | 0.730 | 69204 |
| 2026-09-05T13:10:01.6380347Z | 2026-09-05T13:10:01.6828732Z | sccache stats | 0.001 | 70069 |
| 2026-09-05T12:31:17.7400668Z | 2026-09-05T12:32:20.7473201Z | Dist rust-docs-nightly-x86_64-pc-windows-msvc | 1.050 | 34729 |
| 2026-09-05T12:32:33.1348765Z | 2026-09-05T12:32:40.0461940Z | Dist rust-docs-json-nightly-x86_64-pc-windows-msvc | 0.115 | 34768 |
| 2026-09-05T12:36:47.7431775Z | 2026-09-05T12:37:28.5517913Z | Dist rustc-nightly-x86_64-pc-windows-msvc | 0.680 | 41757 |
| 2026-09-05T12:37:28.5911930Z | 2026-09-05T12:37:33.2522539Z | Dist rustc-codegen-cranelift-nightly-x86_64-pc-windows-msvc | 0.078 | 41761 |
| 2026-09-05T12:37:33.2994262Z | 2026-09-05T12:37:44.6144521Z | Dist rust-std-nightly-x86_64-pc-windows-msvc | 0.189 | 41765 |
| 2026-09-05T12:37:45.4577354Z | 2026-09-05T12:38:48.3089532Z | Dist rustc-dev-nightly-x86_64-pc-windows-msvc | 1.048 | 41769 |
| 2026-09-05T12:38:48.3481458Z | 2026-09-05T12:38:48.3870085Z | Dist rust-analysis-nightly-x86_64-pc-windows-msvc | 0.001 | 41773 |
| 2026-09-05T12:38:50.0706705Z | 2026-09-05T12:39:00.5837306Z | Dist rust-src-nightly | 0.175 | 41814 |
| 2026-09-05T12:39:01.5332935Z | 2026-09-05T12:39:10.5018164Z | Dist cargo-nightly-x86_64-pc-windows-msvc | 0.149 | 42209 |
| 2026-09-05T12:43:44.2058234Z | 2026-09-05T12:43:53.9517667Z | Dist rust-analyzer-nightly-x86_64-pc-windows-msvc | 0.162 | 42712 |
| 2026-09-05T12:44:53.1736138Z | 2026-09-05T12:44:57.4617827Z | Dist rustfmt-nightly-x86_64-pc-windows-msvc | 0.071 | 43010 |
| 2026-09-05T12:47:27.0116000Z | 2026-09-05T12:47:33.6634977Z | Dist clippy-nightly-x86_64-pc-windows-msvc | 0.111 | 43232 |
| 2026-09-05T12:49:04.7943994Z | 2026-09-05T12:49:09.1185870Z | Dist miri-nightly-x86_64-pc-windows-msvc | 0.072 | 43517 |
| 2026-09-05T12:49:09.1597765Z | 2026-09-05T12:49:44.4894927Z | Dist llvm-tools-nightly-x86_64-pc-windows-msvc | 0.589 | 43521 |
| 2026-09-05T12:49:44.5288301Z | 2026-09-05T12:49:45.9617589Z | Dist llvm-bitcode-linker-nightly-x86_64-pc-windows-msvc | 0.024 | 43525 |
| 2026-09-05T12:49:46.9890004Z | 2026-09-05T12:53:46.7768242Z | Dist rust-dev-nightly-x86_64-pc-windows-msvc | 3.996 | 43531 |
| 2026-09-05T12:54:06.4532578Z | 2026-09-05T12:54:12.9932020Z | Dist rust-docs-json-nightly-x86_64-pc-windows-msvc | 0.109 | 43593 |
| 2026-09-05T12:54:13.0307225Z | 2026-09-05T12:57:38.9095692Z | Dist rust-nightly-x86_64-pc-windows-msvc | 3.431 | 43596 |
| 2026-09-05T12:58:23.2649714Z | 2026-09-05T13:00:20.2232473Z | MSI package | 1.949 | 43610 |
| 2026-09-05T13:00:20.2624993Z | 2026-09-05T13:00:37.0337703Z | Dist reproducible-artifacts-nightly-x86_64-pc-windows-msvc | 0.280 | 43615 |
| 2026-09-05T13:00:37.0732649Z | 2026-09-05T13:00:45.3534535Z | Dist bootstrap-nightly-x86_64-pc-windows-msvc | 0.138 | 43619 |

</details>

| opt-dist timer (nested) | Minutes |
|---|---:|
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Build PGO instrumented rustc and LLVM | 40.462 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather rustc profiles | 12.111 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather rustdoc profiles | 1.815 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Gather clippy profiles | 2.488 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) > Build PGO optimized rustc | 16.440 |
| Stage 1 (Rustc + rustdoc + cargo + clippy PGO) | 73.316 |
| Stage 2 (LLVM PGO) > Build PGO instrumented LLVM | 7.360 |
| Stage 2 (LLVM PGO) > Gather profiles | 5.836 |
| Stage 2 (LLVM PGO) | 13.252 |
| Stage 5 (final build) | 43.412 |
| Run tests | 9.271 |

## [auto - i686-msvc-1: 101293559564](https://github.com/rust-lang/rust/actions/runs/33961251131/job/101293559564)

Run 33961251131; raw SHA256 `58889fe3a4641d305cfc15fbd1b39bd72cd7160a75037d6f6e64e2f4bf87dd33`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 1.422 |
| Build support | 1.903 |
| LLVM/LLD | 15.213 |
| Compiler | 56.967 |
| Tools | 39.104 |
| Libraries | 1.733 |
| Tests | 63.700 |
| Docs | 4.408 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-05T10:45:56.2439487Z | 2026-09-05T10:45:56.2471175Z | Run set +e | 0.000 | 1789 |
| 2026-09-05T10:45:58.5100482Z | 2026-09-05T10:45:58.7281482Z | Clock drift check | 0.004 | 1835 |
| 2026-09-05T10:46:01.2370726Z | 2026-09-05T10:46:01.2407404Z | Configure the build | 0.000 | 1841 |
| 2026-09-05T10:46:13.1630059Z | 2026-09-05T10:48:06.6402763Z | Building bootstrap | 1.891 | 1887 |
| 2026-09-05T10:48:11.4789773Z | 2026-09-05T10:48:11.4863127Z | Building LLVM for i686-pc-windows-msvc | 0.000 | 2067 |
| 2026-09-05T10:48:11.4885866Z | 2026-09-05T10:48:11.4892775Z | Building stage1 compiler artifacts (stage0 -> stage1, i686-pc-windows-msvc) | 0.000 | 2069 |
| 2026-09-05T10:48:11.4898807Z | 2026-09-05T10:48:11.4899777Z | Building stage1 codegen backend cranelift (stage0 -> stage1, i686-pc-windows-msvc) | 0.000 | 2072 |
| 2026-09-05T10:48:11.4907289Z | 2026-09-05T10:48:11.4910331Z | Building stage1 lld-wrapper (stage0 -> stage1, i686-pc-windows-msvc) | 0.000 | 2074 |
| 2026-09-05T10:48:11.4919756Z | 2026-09-05T10:48:11.4920957Z | Building stage1 wasm-component-ld (stage0 -> stage1, i686-pc-windows-msvc) | 0.000 | 2076 |
| 2026-09-05T10:48:11.4927150Z | 2026-09-05T10:48:11.4929470Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, i686-pc-windows-msvc) | 0.000 | 2078 |
| 2026-09-05T10:48:11.4942555Z | 2026-09-05T10:48:11.4947386Z | Building stage1 library artifacts (stage1 -> stage1, i686-pc-windows-msvc) | 0.000 | 2080 |
| 2026-09-05T10:48:11.4952601Z | 2026-09-05T10:48:11.4955964Z | Building stage2 compiler artifacts (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2082 |
| 2026-09-05T10:48:11.4961514Z | 2026-09-05T10:48:11.4962419Z | Building stage2 codegen backend cranelift (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2085 |
| 2026-09-05T10:48:11.4967659Z | 2026-09-05T10:48:11.4970146Z | Building stage2 lld-wrapper (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2087 |
| 2026-09-05T10:48:11.4977983Z | 2026-09-05T10:48:11.4980533Z | Building stage2 wasm-component-ld (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2089 |
| 2026-09-05T10:48:11.4985524Z | 2026-09-05T10:48:11.4987923Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2091 |
| 2026-09-05T10:48:11.5006171Z | 2026-09-05T10:48:11.5008403Z | Building stage2 cargo (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2094 |
| 2026-09-05T10:48:11.5013276Z | 2026-09-05T10:48:11.5015591Z | Building stage2 rust-analyzer (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2096 |
| 2026-09-05T10:48:11.5020467Z | 2026-09-05T10:48:11.5022775Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2098 |
| 2026-09-05T10:48:11.5029231Z | 2026-09-05T10:48:11.5031477Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2100 |
| 2026-09-05T10:48:11.5037466Z | 2026-09-05T10:48:11.5039711Z | Building stage2 clippy-driver (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2102 |
| 2026-09-05T10:48:11.5045673Z | 2026-09-05T10:48:11.5048000Z | Building stage2 cargo-clippy (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2104 |
| 2026-09-05T10:48:11.5053437Z | 2026-09-05T10:48:11.5055726Z | Building stage2 rustfmt (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2106 |
| 2026-09-05T10:48:11.5061129Z | 2026-09-05T10:48:11.5064235Z | Building stage2 cargo-fmt (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2108 |
| 2026-09-05T10:48:11.5070637Z | 2026-09-05T10:48:11.5072757Z | Building stage2 miri (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2110 |
| 2026-09-05T10:48:11.5078672Z | 2026-09-05T10:48:11.5080983Z | Building stage2 cargo-miri (stage1 -> stage2, i686-pc-windows-msvc) | 0.000 | 2112 |
| 2026-09-05T10:48:11.5285650Z | 2026-09-05T10:48:11.6166032Z | Display CPU and Memory information | 0.001 | 2115 |
| 2026-09-05T10:48:11.8134398Z | 2026-09-05T10:48:12.0017031Z | Building bootstrap | 0.003 | 2235 |
| 2026-09-05T10:48:15.5385864Z | 2026-09-05T11:03:01.8627464Z | Building LLVM for i686-pc-windows-msvc | 14.772 | 2347 |
| 2026-09-05T11:03:01.9118407Z | 2026-09-05T11:24:52.8840341Z | Building stage1 compiler artifacts (stage0 -> stage1, i686-pc-windows-msvc) | 21.850 | 9530 |
| 2026-09-05T11:24:52.8991622Z | 2026-09-05T11:28:01.0311106Z | Building stage1 codegen backend cranelift (stage0 -> stage1, i686-pc-windows-msvc) | 3.136 | 10321 |
| 2026-09-05T11:28:01.0422168Z | 2026-09-05T11:28:27.4703474Z | Building LLD for i686-pc-windows-msvc | 0.440 | 10443 |
| 2026-09-05T11:28:27.4771054Z | 2026-09-05T11:28:28.5642628Z | Building stage1 lld-wrapper (stage0 -> stage1, i686-pc-windows-msvc) | 0.018 | 10684 |
| 2026-09-05T11:28:28.5753879Z | 2026-09-05T11:30:21.3469874Z | Building stage1 wasm-component-ld (stage0 -> stage1, i686-pc-windows-msvc) | 1.880 | 10693 |
| 2026-09-05T11:30:21.3516138Z | 2026-09-05T11:30:45.6767271Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, i686-pc-windows-msvc) | 0.405 | 10843 |
| 2026-09-05T11:30:45.6888325Z | 2026-09-05T11:32:29.6589366Z | Building stage1 library artifacts (stage1 -> stage1, i686-pc-windows-msvc) | 1.733 | 10924 |
| 2026-09-05T11:32:29.6607078Z | 2026-09-05T12:07:36.7164349Z | Building stage2 compiler artifacts (stage1 -> stage2, i686-pc-windows-msvc) | 35.118 | 10980 |
| 2026-09-05T12:07:36.7202141Z | 2026-09-05T12:12:56.3112161Z | Building stage2 codegen backend cranelift (stage1 -> stage2, i686-pc-windows-msvc) | 5.327 | 11584 |
| 2026-09-05T12:12:56.3133510Z | 2026-09-05T12:12:57.7632217Z | Building stage2 lld-wrapper (stage1 -> stage2, i686-pc-windows-msvc) | 0.024 | 11678 |
| 2026-09-05T12:12:57.7678017Z | 2026-09-05T12:15:50.8597762Z | Building stage2 wasm-component-ld (stage1 -> stage2, i686-pc-windows-msvc) | 2.885 | 11687 |
| 2026-09-05T12:15:50.8619273Z | 2026-09-05T12:16:29.7985954Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, i686-pc-windows-msvc) | 0.649 | 11816 |
| 2026-09-05T12:16:29.8231121Z | 2026-09-05T12:17:15.1886919Z | Building stage1 compiletest (stage0 -> stage1, i686-pc-windows-msvc) | 0.756 | 11903 |
| 2026-09-05T12:17:15.2259056Z | 2026-09-05T12:17:15.4328317Z | Building test helpers for i686-pc-windows-msvc | 0.003 | 12087 |
| 2026-09-05T12:17:15.4524385Z | 2026-09-05T12:42:58.3513715Z | Testing stage2 with compiletest suite=ui mode=ui (i686-pc-windows-msvc) | 25.715 | 12091 |
| 2026-09-05T12:42:58.3846118Z | 2026-09-05T12:43:04.6362587Z | Testing stage2 with compiletest suite=crashes mode=crashes (i686-pc-windows-msvc) | 0.104 | 34279 |
| 2026-09-05T12:43:04.6571569Z | 2026-09-05T12:43:10.1519841Z | Building stage1 coverage-dump (stage0 -> stage1, i686-pc-windows-msvc) | 0.092 | 34494 |
| 2026-09-05T12:43:10.1538363Z | 2026-09-05T12:43:17.0945557Z | Testing stage2 with compiletest suite=coverage mode=coverage-map (i686-pc-windows-msvc) | 0.116 | 34540 |
| 2026-09-05T12:43:17.1146980Z | 2026-09-05T12:43:17.3086906Z | Testing stage2 with compiletest suite=coverage mode=coverage-run (i686-pc-windows-msvc) | 0.003 | 34656 |
| 2026-09-05T12:43:17.3233343Z | 2026-09-05T12:43:41.4316716Z | Testing stage2 with compiletest suite=mir-opt mode=mir-opt (i686-pc-windows-msvc) | 0.402 | 34777 |
| 2026-09-05T12:43:41.4600405Z | 2026-09-05T12:44:30.7695328Z | Testing stage2 with compiletest suite=codegen-llvm mode=codegen (i686-pc-windows-msvc) | 0.822 | 35198 |
| 2026-09-05T12:44:30.7912900Z | 2026-09-05T12:44:33.2002220Z | Testing stage2 with compiletest suite=codegen-units mode=codegen-units (i686-pc-windows-msvc) | 0.040 | 36426 |
| 2026-09-05T12:44:33.2263670Z | 2026-09-05T12:45:23.3859817Z | Testing stage2 with compiletest suite=assembly-llvm mode=assembly (i686-pc-windows-msvc) | 0.836 | 36483 |
| 2026-09-05T12:45:23.4051081Z | 2026-09-05T12:45:59.5822388Z | Testing stage2 with compiletest suite=incremental mode=incremental (i686-pc-windows-msvc) | 0.603 | 37268 |
| 2026-09-05T12:46:01.7565515Z | 2026-09-05T12:46:44.9616832Z | Testing stage2 with compiletest suite=debuginfo mode=debuginfo (i686-pc-windows-msvc) | 0.720 | 37461 |
| 2026-09-05T12:46:45.0323737Z | 2026-09-05T12:47:38.7555206Z | Testing stage2 with compiletest suite=ui-fulldeps mode=ui (i686-pc-windows-msvc) | 0.895 | 37996 |
| 2026-09-05T12:47:38.7794749Z | 2026-09-05T12:52:54.2287793Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, i686-pc-windows-msvc) | 5.257 | 38087 |
| 2026-09-05T12:52:54.2325364Z | 2026-09-05T12:55:31.3502395Z | Testing stage2 with compiletest suite=rustdoc-html mode=rustdoc-html (i686-pc-windows-msvc) | 2.619 | 38294 |
| 2026-09-05T12:55:31.3734527Z | 2026-09-05T12:55:31.5428062Z | Testing stage2 with compiletest suite=coverage-run-rustdoc mode=coverage-run (i686-pc-windows-msvc) | 0.003 | 39108 |
| 2026-09-05T12:55:31.5630804Z | 2026-09-05T12:55:36.0947348Z | Testing stage2 with compiletest suite=pretty mode=pretty (i686-pc-windows-msvc) | 0.076 | 39122 |
| 2026-09-05T12:55:36.1167124Z | 2026-09-05T13:10:38.1639576Z | Testing stage2 {alloc, alloctests, compiler_builtins, core, coretests, panic_abort, panic_unwind, proc_macro, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} (i686-pc-windows-msvc) | 15.034 | 39253 |
| 2026-09-05T13:10:38.1701708Z | 2026-09-05T13:12:24.7634204Z | Testing stage1 tidy (i686-pc-windows-msvc) | 1.777 | 55303 |
| 2026-09-05T13:12:24.7679267Z | 2026-09-05T13:15:03.8016268Z | Building stage2 error_index_generator (stage1 -> stage2, i686-pc-windows-msvc) | 2.651 | 55612 |
| 2026-09-05T13:15:03.8135164Z | 2026-09-05T13:15:03.9115738Z | Testing stage2 error-index (i686-pc-windows-msvc) | 0.002 | 55895 |
| 2026-09-05T13:16:00.5373066Z | 2026-09-05T13:17:02.5233560Z | Testing stage1 stdarch-verify (i686-pc-windows-msvc) | 1.033 | 57025 |
| 2026-09-05T13:17:02.5351462Z | 2026-09-05T13:18:47.9885178Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage2 -> stage2, i686-pc-windows-msvc) | 1.758 | 57110 |
| 2026-09-05T13:18:47.9957741Z | 2026-09-05T13:19:43.4171468Z | Testing stage2 rustdoc-js-std (i686-pc-windows-msvc) | 0.924 | 57164 |
| 2026-09-05T13:19:43.4536237Z | 2026-09-05T13:20:08.8954771Z | Testing stage2 with compiletest suite=rustdoc-js mode=rustdoc-js (i686-pc-windows-msvc) | 0.424 | 57236 |
| 2026-09-05T13:20:08.9261333Z | 2026-09-05T13:20:52.3623585Z | Testing stage2 with compiletest suite=rustdoc-ui mode=ui (i686-pc-windows-msvc) | 0.724 | 57327 |
| 2026-09-05T13:20:52.3916940Z | 2026-09-05T13:21:28.8372943Z | Building stage1 jsondocck (stage0 -> stage1, i686-pc-windows-msvc) | 0.607 | 57786 |
| 2026-09-05T13:21:28.8389725Z | 2026-09-05T13:21:46.0370671Z | Building stage1 jsondoclint (stage0 -> stage1, i686-pc-windows-msvc) | 0.287 | 57920 |
| 2026-09-05T13:21:46.0386687Z | 2026-09-05T13:22:06.7550411Z | Testing stage2 with compiletest suite=rustdoc-json mode=rustdoc-json (i686-pc-windows-msvc) | 0.345 | 57974 |
| 2026-09-05T13:22:06.7937891Z | 2026-09-05T13:22:23.0358787Z | Building stage1 run_make_support (stage0 -> stage1, i686-pc-windows-msvc) | 0.271 | 58181 |
| 2026-09-05T13:22:23.0382937Z | 2026-09-05T13:27:09.7155448Z | Testing stage2 with compiletest suite=run-make mode=run-make (i686-pc-windows-msvc) | 4.778 | 58264 |
| 2026-09-05T13:27:09.7542463Z | 2026-09-05T13:44:40.4048752Z | Building stage2 cargo (stage1 -> stage2, i686-pc-windows-msvc) | 17.511 | 58802 |
| 2026-09-05T13:44:40.4079366Z | 2026-09-05T13:50:22.8143063Z | Testing stage2 with compiletest suite=run-make-cargo mode=run-make (i686-pc-windows-msvc) | 5.707 | 59738 |

</details>

## [auto - dist-aarch64-msvc: 101293559581](https://github.com/rust-lang/rust/actions/runs/33961251131/job/101293559581)

Run 33961251131; raw SHA256 `f379f38ce011d24a77ed20ae1cc904271e47bf0feceb3557754d9a80045d596c`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 5.838 |
| Build support | 5.388 |
| LLVM/LLD | 12.302 |
| Compiler | 22.065 |
| Tools | 27.293 |
| Libraries | 1.903 |
| Docs | 10.007 |
| Packaging | 26.488 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-05T10:52:20.0152953Z | 2026-09-05T10:52:20.0192109Z | Run set +e | 0.000 | 1851 |
| 2026-09-05T10:52:23.3797621Z | 2026-09-05T10:52:23.7308166Z | Clock drift check | 0.006 | 1899 |
| 2026-09-05T10:52:25.7467037Z | 2026-09-05T10:52:25.7486647Z | Configure the build | 0.000 | 1905 |
| 2026-09-05T10:52:35.4082879Z | 2026-09-05T10:53:45.1889625Z | Building bootstrap | 1.163 | 1950 |
| 2026-09-05T10:53:46.8373493Z | 2026-09-05T10:53:46.8470911Z | Building LLVM for aarch64-pc-windows-msvc | 0.000 | 2130 |
| 2026-09-05T10:53:46.8510239Z | 2026-09-05T10:53:46.8522050Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2132 |
| 2026-09-05T10:53:46.8533758Z | 2026-09-05T10:53:46.9272798Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.001 | 2135 |
| 2026-09-05T10:53:46.9287237Z | 2026-09-05T10:53:46.9289414Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2137 |
| 2026-09-05T10:53:46.9295939Z | 2026-09-05T10:53:46.9299530Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2139 |
| 2026-09-05T10:53:46.9316956Z | 2026-09-05T10:53:46.9322445Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2141 |
| 2026-09-05T10:53:46.9327874Z | 2026-09-05T10:53:46.9331896Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2143 |
| 2026-09-05T10:53:46.9339411Z | 2026-09-05T10:53:46.9342838Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2146 |
| 2026-09-05T10:53:46.9353228Z | 2026-09-05T10:53:46.9355901Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2148 |
| 2026-09-05T10:53:46.9359829Z | 2026-09-05T10:53:46.9362263Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2150 |
| 2026-09-05T10:53:46.9416802Z | 2026-09-05T10:53:46.9422847Z | Building stage1 library artifacts (stage1:aarch64-pc-windows-msvc -> stage1:arm64ec-pc-windows-msvc) | 0.000 | 2153 |
| 2026-09-05T10:53:46.9504085Z | 2026-09-05T10:53:46.9505592Z | Building stage2 cargo (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2156 |
| 2026-09-05T10:53:46.9510781Z | 2026-09-05T10:53:46.9513215Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2158 |
| 2026-09-05T10:53:46.9518088Z | 2026-09-05T10:53:46.9521141Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2160 |
| 2026-09-05T10:53:46.9529385Z | 2026-09-05T10:53:46.9531231Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2162 |
| 2026-09-05T10:53:46.9538540Z | 2026-09-05T10:53:46.9540959Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2164 |
| 2026-09-05T10:53:46.9547168Z | 2026-09-05T10:53:46.9551516Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2166 |
| 2026-09-05T10:53:46.9556517Z | 2026-09-05T10:53:46.9559080Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2168 |
| 2026-09-05T10:53:46.9565314Z | 2026-09-05T10:53:46.9567557Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2170 |
| 2026-09-05T10:53:46.9573716Z | 2026-09-05T10:53:46.9576062Z | Building stage2 miri (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2172 |
| 2026-09-05T10:53:46.9583649Z | 2026-09-05T10:53:46.9585797Z | Building stage2 cargo-miri (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2174 |
| 2026-09-05T10:53:46.9871865Z | 2026-09-05T10:53:47.2579142Z | Display CPU and Memory information | 0.005 | 2177 |
| 2026-09-05T10:53:47.5189976Z | 2026-09-05T10:53:47.7177450Z | Building bootstrap | 0.003 | 2285 |
| 2026-09-05T10:53:49.1702314Z | 2026-09-05T11:05:40.2322377Z | Building LLVM for aarch64-pc-windows-msvc | 11.851 | 2297 |
| 2026-09-05T11:05:40.3336049Z | 2026-09-05T11:16:51.3495149Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 11.184 | 9473 |
| 2026-09-05T11:16:51.3661418Z | 2026-09-05T11:17:18.4110456Z | Building LLD for aarch64-pc-windows-msvc | 0.451 | 10265 |
| 2026-09-05T11:17:18.4145838Z | 2026-09-05T11:17:20.3649723Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.033 | 10504 |
| 2026-09-05T11:17:20.3799984Z | 2026-09-05T11:18:20.9148004Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.009 | 10513 |
| 2026-09-05T11:18:20.9253746Z | 2026-09-05T11:18:35.0792098Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.236 | 10663 |
| 2026-09-05T11:18:35.1024452Z | 2026-09-05T11:19:33.3023900Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.970 | 10743 |
| 2026-09-05T11:19:33.3119328Z | 2026-09-05T11:20:23.6796878Z | Building stage1 unstable-book-gen (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.839 | 10807 |
| 2026-09-05T11:20:25.5459981Z | 2026-09-05T11:21:55.3289165Z | Building stage1 rustbook (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.496 | 11062 |
| 2026-09-05T11:21:58.9362430Z | 2026-09-05T11:22:54.8887210Z | Building stage1 library artifacts (stage1:aarch64-pc-windows-msvc -> stage1:arm64ec-pc-windows-msvc) | 0.933 | 11502 |
| 2026-09-05T11:23:01.9484342Z | 2026-09-05T11:23:01.9662097Z | Documenting stage2 book redirect pages (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 11597 |
| 2026-09-05T11:23:01.9662790Z | 2026-09-05T11:24:56.4245378Z | Building stage1 rustdoc-tool-binary (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.908 | 11601 |
| 2026-09-05T11:24:56.4250164Z | 2026-09-05T11:24:59.7347397Z | Documenting stage2 book redirect pages (stage1 -> stage2, aarch64-pc-windows-msvc) (continued) | 0.055 | 11806 |
| 2026-09-05T11:25:01.3392299Z | 2026-09-05T11:25:04.5524837Z | Documenting stage2 book redirect pages (stage1:aarch64-pc-windows-msvc -> stage2:arm64ec-pc-windows-msvc) | 0.054 | 11839 |
| 2026-09-05T11:25:04.5556677Z | 2026-09-05T11:25:05.7961105Z | Documenting stage2 standalone (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.021 | 11843 |
| 2026-09-05T11:25:05.7975785Z | 2026-09-05T11:25:07.0639846Z | Documenting stage2 standalone (stage1:aarch64-pc-windows-msvc -> stage2:arm64ec-pc-windows-msvc) | 0.021 | 11847 |
| 2026-09-05T11:25:07.0731332Z | 2026-09-05T11:27:32.3660460Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage1 -> stage1, aarch64-pc-windows-msvc) | 2.422 | 11851 |
| 2026-09-05T11:27:32.3694346Z | 2026-09-05T11:29:52.1202737Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage1:aarch64-pc-windows-msvc -> stage1:arm64ec-pc-windows-msvc) | 2.329 | 11906 |
| 2026-09-05T11:29:52.1381878Z | 2026-09-05T11:40:45.0214160Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 10.881 | 11966 |
| 2026-09-05T11:40:45.0263410Z | 2026-09-05T11:40:46.1249320Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.018 | 12571 |
| 2026-09-05T11:40:46.1346394Z | 2026-09-05T11:41:45.3020000Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.986 | 12580 |
| 2026-09-05T11:41:45.3046814Z | 2026-09-05T11:41:59.3831942Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.235 | 12709 |
| 2026-09-05T11:41:59.3894095Z | 2026-09-05T11:42:55.0399009Z | Building stage2 error_index_generator (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.928 | 12787 |
| 2026-09-05T11:43:27.8217623Z | 2026-09-05T11:43:32.8936875Z | Building stage1 lint-docs (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.085 | 13227 |
| 2026-09-05T11:43:32.9469934Z | 2026-09-05T11:44:03.9540913Z | Running stage2 lint-docs (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.517 | 13258 |
| 2026-09-05T11:44:08.4536042Z | 2026-09-05T11:44:08.7170281Z | Documenting stage2 releases (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.004 | 13361 |
| 2026-09-05T11:44:08.7176102Z | 2026-09-05T11:44:08.9421989Z | Documenting stage2 releases (stage1:aarch64-pc-windows-msvc -> stage2:arm64ec-pc-windows-msvc) | 0.004 | 13365 |
| 2026-09-05T11:44:52.0964421Z | 2026-09-05T11:45:18.6829492Z | Building stage1 rust-installer (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.443 | 13370 |
| 2026-09-05T11:50:05.2643511Z | 2026-09-05T11:50:22.8380416Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.293 | 13461 |
| 2026-09-05T11:50:30.8346310Z | 2026-09-05T11:50:46.2125831Z | Documenting stage1 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage1:aarch64-pc-windows-msvc -> stage1:arm64ec-pc-windows-msvc) | 0.256 | 13500 |
| 2026-09-05T11:50:53.7954917Z | 2026-09-05T11:52:37.1786590Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.723 | 13544 |
| 2026-09-05T11:52:37.1909677Z | 2026-09-05T11:53:28.1548783Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.849 | 13725 |
| 2026-09-05T11:53:28.2475335Z | 2026-09-05T11:57:33.8197361Z | Vendoring sources to "C:\\a\\rust\\rust" | 4.093 | 13923 |
| 2026-09-05T11:57:33.9366373Z | 2026-09-05T11:57:33.9394831Z | generate-copyright | 0.000 | 16518 |
| 2026-09-05T11:57:33.9395461Z | 2026-09-05T11:58:14.0355941Z | Building stage1 generate-copyright (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.668 | 16522 |
| 2026-09-05T11:58:14.0360396Z | 2026-09-05T11:58:19.4523715Z | generate-copyright (continued) | 0.090 | 16653 |
| 2026-09-05T12:01:26.6128567Z | 2026-09-05T12:01:28.0842815Z | Vendoring sources to "C:\\a\\rust\\rust\\build\\tmp\\tarball\\rust-src\\image\\lib/rustlib/src/rust" | 0.025 | 21047 |
| 2026-09-05T12:01:44.4227381Z | 2026-09-05T12:08:25.9886425Z | Building stage2 cargo (stage1 -> stage2, aarch64-pc-windows-msvc) | 6.693 | 21089 |
| 2026-09-05T12:08:37.6661511Z | 2026-09-05T12:16:04.3913513Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-pc-windows-msvc) | 7.445 | 21810 |
| 2026-09-05T12:16:16.4313533Z | 2026-09-05T12:17:26.1138281Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.161 | 22308 |
| 2026-09-05T12:17:26.1181202Z | 2026-09-05T12:17:26.7744538Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.011 | 22481 |
| 2026-09-05T12:17:32.2973587Z | 2026-09-05T12:19:44.5264842Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-pc-windows-msvc) | 2.204 | 22595 |
| 2026-09-05T12:19:44.5316479Z | 2026-09-05T12:19:45.1957382Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.011 | 22763 |
| 2026-09-05T12:19:53.8523471Z | 2026-09-05T12:21:21.3272170Z | Building stage2 miri (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.458 | 22874 |
| 2026-09-05T12:21:21.3306745Z | 2026-09-05T12:21:33.3697122Z | Building stage2 cargo-miri (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.201 | 23066 |
| 2026-09-05T12:27:45.2568184Z | 2026-09-05T12:28:26.2548417Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, profiler_builtins, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in JSON format (stage2 -> stage2, aarch64-pc-windows-msvc) | 0.683 | 23163 |
| 2026-09-05T12:43:35.6481727Z | 2026-09-05T12:43:35.8501752Z | sccache stats | 0.003 | 23246 |
| 2026-09-05T11:45:18.7409994Z | 2026-09-05T11:47:16.9208692Z | Dist rust-docs-nightly-aarch64-pc-windows-msvc | 1.970 | 13452 |
| 2026-09-05T11:48:02.8204554Z | 2026-09-05T11:50:05.2577187Z | Dist rust-docs-nightly-arm64ec-pc-windows-msvc | 2.041 | 13456 |
| 2026-09-05T11:50:22.9190520Z | 2026-09-05T11:50:30.8307086Z | Dist rust-docs-json-nightly-aarch64-pc-windows-msvc | 0.132 | 13495 |
| 2026-09-05T11:50:46.2910907Z | 2026-09-05T11:50:53.7823605Z | Dist rust-docs-json-nightly-arm64ec-pc-windows-msvc | 0.125 | 13534 |
| 2026-09-05T11:58:19.5578510Z | 2026-09-05T11:59:17.1554623Z | Dist rustc-nightly-aarch64-pc-windows-msvc | 0.960 | 21022 |
| 2026-09-05T11:59:17.2753940Z | 2026-09-05T11:59:31.8676595Z | Dist rust-std-nightly-aarch64-pc-windows-msvc | 0.243 | 21026 |
| 2026-09-05T11:59:32.3534571Z | 2026-09-05T11:59:46.3719858Z | Dist rust-std-nightly-arm64ec-pc-windows-msvc | 0.234 | 21030 |
| 2026-09-05T11:59:51.5750722Z | 2026-09-05T12:01:23.6925698Z | Dist rustc-dev-nightly-aarch64-pc-windows-msvc | 1.535 | 21034 |
| 2026-09-05T12:01:23.7726327Z | 2026-09-05T12:01:23.8334392Z | Dist rust-analysis-nightly-aarch64-pc-windows-msvc | 0.001 | 21038 |
| 2026-09-05T12:01:23.9150959Z | 2026-09-05T12:01:23.9798399Z | Dist rust-analysis-nightly-arm64ec-pc-windows-msvc | 0.001 | 21042 |
| 2026-09-05T12:01:28.1869070Z | 2026-09-05T12:01:44.4191510Z | Dist rust-src-nightly | 0.271 | 21083 |
| 2026-09-05T12:08:26.1039968Z | 2026-09-05T12:08:37.6562481Z | Dist cargo-nightly-aarch64-pc-windows-msvc | 0.193 | 21804 |
| 2026-09-05T12:16:04.4757484Z | 2026-09-05T12:16:16.4252354Z | Dist rust-analyzer-nightly-aarch64-pc-windows-msvc | 0.199 | 22302 |
| 2026-09-05T12:17:26.8557343Z | 2026-09-05T12:17:32.2952020Z | Dist rustfmt-nightly-aarch64-pc-windows-msvc | 0.091 | 22589 |
| 2026-09-05T12:19:45.2812797Z | 2026-09-05T12:19:53.8492827Z | Dist clippy-nightly-aarch64-pc-windows-msvc | 0.143 | 22868 |
| 2026-09-05T12:21:33.4570717Z | 2026-09-05T12:21:38.3378323Z | Dist miri-nightly-aarch64-pc-windows-msvc | 0.081 | 23142 |
| 2026-09-05T12:21:38.4364115Z | 2026-09-05T12:22:22.2911570Z | Dist llvm-tools-nightly-aarch64-pc-windows-msvc | 0.731 | 23146 |
| 2026-09-05T12:22:22.3769554Z | 2026-09-05T12:22:24.0049036Z | Dist llvm-bitcode-linker-nightly-aarch64-pc-windows-msvc | 0.027 | 23150 |
| 2026-09-05T12:22:27.2407919Z | 2026-09-05T12:27:45.2222155Z | Dist rust-dev-nightly-aarch64-pc-windows-msvc | 5.300 | 23156 |
| 2026-09-05T12:28:26.5097916Z | 2026-09-05T12:28:35.3883248Z | Dist rust-docs-json-nightly-aarch64-pc-windows-msvc | 0.148 | 23218 |
| 2026-09-05T12:28:35.4856871Z | 2026-09-05T12:34:52.8752071Z | Dist rust-nightly-aarch64-pc-windows-msvc | 6.290 | 23221 |
| 2026-09-05T12:37:48.7792473Z | 2026-09-05T12:43:27.2322469Z | MSI package | 5.641 | 23235 |
| 2026-09-05T12:43:27.4128377Z | 2026-09-05T12:43:35.4175147Z | Dist bootstrap-nightly-aarch64-pc-windows-msvc | 0.133 | 23242 |

</details>

## [auto - aarch64-msvc-2: 101293559594](https://github.com/rust-lang/rust/actions/runs/33961251131/job/101293559594)

Run 33961251131; raw SHA256 `c628f45937852daa2d8e4ffb0d629aad0fd5fe87c64e59b5946bc3d75c562d3d`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 8.046 |
| Build support | 1.139 |
| LLVM/LLD | 13.544 |
| Compiler | 32.422 |
| Tools | 10.647 |
| Libraries | 1.331 |
| Tests | 29.672 |
| Docs | 3.483 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-05T10:53:16.1718115Z | 2026-09-05T10:53:16.1752839Z | Run set +e | 0.000 | 1814 |
| 2026-09-05T10:53:19.6834742Z | 2026-09-05T10:53:19.9106868Z | Clock drift check | 0.004 | 1860 |
| 2026-09-05T10:53:22.1687484Z | 2026-09-05T10:53:22.1707407Z | Configure the build | 0.000 | 1866 |
| 2026-09-05T10:53:31.8733086Z | 2026-09-05T10:54:39.5454121Z | Building bootstrap | 1.128 | 1911 |
| 2026-09-05T10:54:41.4947546Z | 2026-09-05T10:54:41.5032234Z | Building LLVM for aarch64-pc-windows-msvc | 0.000 | 2091 |
| 2026-09-05T10:54:41.5067569Z | 2026-09-05T10:54:41.5078922Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2093 |
| 2026-09-05T10:54:41.5086923Z | 2026-09-05T10:54:41.5087620Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2096 |
| 2026-09-05T10:54:41.5096835Z | 2026-09-05T10:54:41.5132672Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2098 |
| 2026-09-05T10:54:41.5143715Z | 2026-09-05T10:54:41.5147008Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2100 |
| 2026-09-05T10:54:41.5152303Z | 2026-09-05T10:54:41.5155055Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2102 |
| 2026-09-05T10:54:41.5172913Z | 2026-09-05T10:54:41.5178914Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2104 |
| 2026-09-05T10:54:41.5184688Z | 2026-09-05T10:54:41.5189407Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2106 |
| 2026-09-05T10:54:41.5196372Z | 2026-09-05T10:54:41.5197004Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2109 |
| 2026-09-05T10:54:41.5203353Z | 2026-09-05T10:54:41.5206982Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2111 |
| 2026-09-05T10:54:41.5218060Z | 2026-09-05T10:54:41.5220960Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2113 |
| 2026-09-05T10:54:41.5225616Z | 2026-09-05T10:54:41.5228523Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2115 |
| 2026-09-05T10:54:41.5252303Z | 2026-09-05T10:54:41.5255065Z | Building stage2 cargo (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2118 |
| 2026-09-05T10:54:41.5260288Z | 2026-09-05T10:54:41.5262945Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2120 |
| 2026-09-05T10:54:41.5269345Z | 2026-09-05T10:54:41.5272076Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2122 |
| 2026-09-05T10:54:41.5279705Z | 2026-09-05T10:54:41.5282546Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2124 |
| 2026-09-05T10:54:41.5290245Z | 2026-09-05T10:54:41.5292884Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2126 |
| 2026-09-05T10:54:41.5299049Z | 2026-09-05T10:54:41.5301874Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2128 |
| 2026-09-05T10:54:41.5308644Z | 2026-09-05T10:54:41.5311306Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2130 |
| 2026-09-05T10:54:41.5317719Z | 2026-09-05T10:54:41.5320404Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2132 |
| 2026-09-05T10:54:41.5326848Z | 2026-09-05T10:54:41.5329975Z | Building stage2 miri (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2134 |
| 2026-09-05T10:54:41.5336967Z | 2026-09-05T10:54:41.5339703Z | Building stage2 cargo-miri (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2136 |
| 2026-09-05T10:54:41.5593685Z | 2026-09-05T10:54:41.8112403Z | Display CPU and Memory information | 0.004 | 2139 |
| 2026-09-05T10:54:45.7543473Z | 2026-09-05T10:54:45.9337897Z | Building bootstrap | 0.003 | 2247 |
| 2026-09-05T10:54:47.3564451Z | 2026-09-05T10:55:47.8777584Z | Building stage1 tidy (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.009 | 2261 |
| 2026-09-05T11:01:05.9532561Z | 2026-09-05T11:14:08.7394913Z | Building LLVM for aarch64-pc-windows-msvc | 13.046 | 3202 |
| 2026-09-05T11:14:09.0268745Z | 2026-09-05T11:27:56.4417266Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 13.790 | 10374 |
| 2026-09-05T11:27:56.4639755Z | 2026-09-05T11:29:47.9447366Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.858 | 10978 |
| 2026-09-05T11:29:47.9752650Z | 2026-09-05T11:30:17.8254865Z | Building LLD for aarch64-pc-windows-msvc | 0.498 | 11072 |
| 2026-09-05T11:30:20.3902014Z | 2026-09-05T11:30:22.0831329Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.028 | 11313 |
| 2026-09-05T11:30:22.1010820Z | 2026-09-05T11:31:18.8796860Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.946 | 11322 |
| 2026-09-05T11:31:18.8881616Z | 2026-09-05T11:31:32.4904680Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.227 | 11431 |
| 2026-09-05T11:31:32.5288594Z | 2026-09-05T11:32:51.9703394Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 1.324 | 11514 |
| 2026-09-05T11:32:52.0385329Z | 2026-09-05T11:51:29.9236616Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 18.631 | 11569 |
| 2026-09-05T11:51:29.9286130Z | 2026-09-05T11:54:23.2600073Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-pc-windows-msvc) | 2.889 | 12173 |
| 2026-09-05T11:54:23.2631892Z | 2026-09-05T11:54:24.6170117Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.023 | 12267 |
| 2026-09-05T11:54:24.6271325Z | 2026-09-05T11:55:54.5977001Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.500 | 12276 |
| 2026-09-05T11:55:54.6004115Z | 2026-09-05T11:56:16.3129679Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.362 | 12405 |
| 2026-09-05T11:56:16.3336556Z | 2026-09-05T11:56:16.7481569Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.007 | 12498 |
| 2026-09-05T11:56:16.7521036Z | 2026-09-05T11:58:01.6401350Z | Building stage1 rustdoc-tool-binary (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.748 | 12532 |
| 2026-09-05T11:58:01.6623226Z | 2026-09-05T12:04:02.2317324Z | Testing stage2 {rustc-main, rustc_abi, rustc_arena, rustc_ast, rustc_ast_ir, rustc_ast_lowering, rustc_ast_passes, rustc_ast_pretty, rustc_attr_ir, rustc_attr_parsing, rustc_baked_icu_data, rustc_borrowck, rustc_builtin_macros, rustc_codegen_llvm, rustc_codegen_ssa, rustc_const_eval, rustc_crate_store, rustc_data_structures, rustc_driver, rustc_driver_impl, rustc_error_codes, rustc_error_messages, rustc_errors, rustc_expand, rustc_feature, rustc_fs_util, rustc_graphviz, rustc_hashes, rustc_hir, rustc_hir_analysis, rustc_hir_id, rustc_hir_pretty, rustc_hir_typeck, rustc_incremental, rustc_index, rustc_index_macros, rustc_infer, rustc_interface, rustc_lexer, rustc_lint, rustc_lint_defs, rustc_llvm, rustc_log, rustc_macros, rustc_metadata, rustc_middle, rustc_mir_build, rustc_mir_dataflow, rustc_mir_transform, rustc_monomorphize, rustc_next_trait_solver, rustc_parse, rustc_parse_format, rustc_passes, rustc_pattern_analysis, rustc_privacy, rustc_proc_macro, rustc_public, rustc_public_bridge, rustc_query_impl, rustc_resolve, rustc_sanitizers, rustc_serialize, rustc_session, rustc_span, rustc_structures, rustc_symbol_mangling, rustc_target, rustc_thread_pool, rustc_trait_selection, rustc_traits, rustc_transmute, rustc_ty_utils, rustc_ty_walk, rustc_type_ir, rustc_type_ir_macros, rustc_windows_rc} (aarch64-pc-windows-msvc) | 6.009 | 12720 |
| 2026-09-05T12:04:02.2436546Z | 2026-09-05T12:06:58.8818684Z | Testing stage2 rustdoc (aarch64-pc-windows-msvc) | 2.944 | 16101 |
| 2026-09-05T12:06:58.8884502Z | 2026-09-05T12:07:39.6993585Z | Testing stage2 rustdoc-json-types (aarch64-pc-windows-msvc) | 0.680 | 16455 |
| 2026-09-05T12:07:39.7028015Z | 2026-09-05T12:07:51.0003523Z | Testing stage1 coverage-dump (aarch64-pc-windows-msvc) | 0.188 | 16581 |
| 2026-09-05T12:07:51.0019069Z | 2026-09-05T12:08:03.5951255Z | Testing stage1 jsondoclint (aarch64-pc-windows-msvc) | 0.210 | 16640 |
| 2026-09-05T12:08:03.5966081Z | 2026-09-05T12:08:06.6609912Z | Testing stage1 replace-version-placeholder (aarch64-pc-windows-msvc) | 0.051 | 16713 |
| 2026-09-05T12:08:06.6629717Z | 2026-09-05T12:08:16.1392399Z | Testing stage1 remote-test-client (aarch64-pc-windows-msvc) | 0.158 | 16849 |
| 2026-09-05T12:08:16.1406042Z | 2026-09-05T12:08:17.3255030Z | Testing stage2 platform support check (aarch64-pc-windows-msvc) | 0.020 | 16895 |
| 2026-09-05T12:08:17.3302436Z | 2026-09-05T12:26:15.3284720Z | Testing stage2 rust-analyzer (aarch64-pc-windows-msvc) | 17.967 | 16903 |
| 2026-09-05T12:26:15.3376407Z | 2026-09-05T12:27:38.8135832Z | Building stage2 error_index_generator (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.391 | 26186 |
| 2026-09-05T12:27:38.8151923Z | 2026-09-05T12:27:38.8624541Z | Testing stage2 error-index (aarch64-pc-windows-msvc) | 0.001 | 26391 |
| 2026-09-05T12:27:38.8990399Z | 2026-09-05T12:27:40.9263565Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.034 | 26402 |
| 2026-09-05T12:28:30.3079219Z | 2026-09-05T12:28:37.1679165Z | Testing stage2 book rustdoc (aarch64-pc-windows-msvc) | 0.114 | 27635 |
| 2026-09-05T12:28:37.1702942Z | 2026-09-05T12:28:57.0036007Z | Testing stage2 book unstable-book (aarch64-pc-windows-msvc) | 0.331 | 27839 |
| 2026-09-05T12:28:57.0045509Z | 2026-09-05T12:29:06.3946146Z | Testing stage2 book rustc (aarch64-pc-windows-msvc) | 0.157 | 28433 |
| 2026-09-05T12:29:06.4949242Z | 2026-09-05T12:29:10.1587531Z | Building stage1 lint-docs (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.061 | 29087 |
| 2026-09-05T12:29:10.2109907Z | 2026-09-05T12:29:44.1702129Z | Running stage2 lint-docs (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.566 | 29117 |
| 2026-09-05T12:29:44.1730503Z | 2026-09-05T12:30:52.2239304Z | Building stage1 rustbook (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.134 | 29122 |
| 2026-09-05T12:30:53.1953175Z | 2026-09-05T12:30:54.6351906Z | Building stage1 rustdoc-themes (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.024 | 29472 |
| 2026-09-05T12:30:54.7697545Z | 2026-09-05T12:31:20.1632814Z | Testing stage1 rust-installer (aarch64-pc-windows-msvc) | 0.423 | 29487 |
| 2026-09-05T12:31:20.1653416Z | 2026-09-05T12:32:05.1715591Z | Testing stage3 test-float-parse (aarch64-pc-windows-msvc) | 0.750 | 29584 |

</details>

## [auto - aarch64-msvc-1: 101293559600](https://github.com/rust-lang/rust/actions/runs/33961251131/job/101293559600)

Run 33961251131; raw SHA256 `9f43caebb4c5c1bc92d715e9bd783519dc593d7e54ecf0d6f1eca858bc2fa35b`.

| Category | Exclusive minutes |
|---|---:|
| Unresolved build | 1.653 |
| Build support | 1.158 |
| LLVM/LLD | 12.912 |
| Compiler | 31.430 |
| Tools | 22.537 |
| Libraries | 1.383 |
| Tests | 50.660 |
| Docs | 4.233 |

<details><summary>All observed bootstrap intervals</summary>

| Start UTC | End UTC | Marker | Minutes | Log line |
|---|---|---|---:|---:|
| 2026-09-05T10:51:59.8169797Z | 2026-09-05T10:51:59.8205378Z | Run set +e | 0.000 | 1806 |
| 2026-09-05T10:52:03.0379944Z | 2026-09-05T10:52:03.2584691Z | Clock drift check | 0.004 | 1852 |
| 2026-09-05T10:52:04.9871643Z | 2026-09-05T10:52:04.9898631Z | Configure the build | 0.000 | 1858 |
| 2026-09-05T10:52:14.4479265Z | 2026-09-05T10:53:23.1341691Z | Building bootstrap | 1.145 | 1903 |
| 2026-09-05T10:53:24.8375946Z | 2026-09-05T10:53:24.8472806Z | Building LLVM for aarch64-pc-windows-msvc | 0.000 | 2083 |
| 2026-09-05T10:53:24.8510143Z | 2026-09-05T10:53:24.8521840Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2085 |
| 2026-09-05T10:53:24.8530273Z | 2026-09-05T10:53:24.8530899Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2088 |
| 2026-09-05T10:53:24.8540743Z | 2026-09-05T10:53:24.8567201Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2090 |
| 2026-09-05T10:53:24.8578711Z | 2026-09-05T10:53:24.8582476Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2092 |
| 2026-09-05T10:53:24.8587815Z | 2026-09-05T10:53:24.8590691Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2094 |
| 2026-09-05T10:53:24.8608935Z | 2026-09-05T10:53:24.8614946Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 0.000 | 2096 |
| 2026-09-05T10:53:24.8621061Z | 2026-09-05T10:53:24.8625630Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2098 |
| 2026-09-05T10:53:24.8633426Z | 2026-09-05T10:53:24.8634370Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2101 |
| 2026-09-05T10:53:24.8641004Z | 2026-09-05T10:53:24.8644755Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2103 |
| 2026-09-05T10:53:24.8655841Z | 2026-09-05T10:53:24.8658994Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2105 |
| 2026-09-05T10:53:24.8669767Z | 2026-09-05T10:53:24.8670499Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2107 |
| 2026-09-05T10:53:24.8691364Z | 2026-09-05T10:53:24.8694127Z | Building stage2 cargo (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2110 |
| 2026-09-05T10:53:24.8699694Z | 2026-09-05T10:53:24.8702490Z | Building stage2 rust-analyzer (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2112 |
| 2026-09-05T10:53:24.8707815Z | 2026-09-05T10:53:24.8710562Z | Building stage2 rust-analyzer-proc-macro-srv (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2114 |
| 2026-09-05T10:53:24.8718537Z | 2026-09-05T10:53:24.8721376Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2116 |
| 2026-09-05T10:53:24.8728934Z | 2026-09-05T10:53:24.8731666Z | Building stage2 clippy-driver (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2118 |
| 2026-09-05T10:53:24.8737904Z | 2026-09-05T10:53:24.8740888Z | Building stage2 cargo-clippy (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2120 |
| 2026-09-05T10:53:24.8747299Z | 2026-09-05T10:53:24.8749920Z | Building stage2 rustfmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2122 |
| 2026-09-05T10:53:24.8756195Z | 2026-09-05T10:53:24.8759187Z | Building stage2 cargo-fmt (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2124 |
| 2026-09-05T10:53:24.8765798Z | 2026-09-05T10:53:24.8768735Z | Building stage2 miri (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2126 |
| 2026-09-05T10:53:24.8776326Z | 2026-09-05T10:53:24.8779131Z | Building stage2 cargo-miri (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.000 | 2128 |
| 2026-09-05T10:53:24.9041403Z | 2026-09-05T10:53:25.1767773Z | Display CPU and Memory information | 0.005 | 2131 |
| 2026-09-05T10:53:25.5571774Z | 2026-09-05T10:53:25.7490491Z | Building bootstrap | 0.003 | 2239 |
| 2026-09-05T10:53:30.2525970Z | 2026-09-05T11:05:54.4522765Z | Building LLVM for aarch64-pc-windows-msvc | 12.403 | 2351 |
| 2026-09-05T11:05:54.5827754Z | 2026-09-05T11:18:12.2346791Z | Building stage1 compiler artifacts (stage0 -> stage1, aarch64-pc-windows-msvc) | 12.294 | 9534 |
| 2026-09-05T11:18:12.2524910Z | 2026-09-05T11:20:08.9767046Z | Building stage1 codegen backend cranelift (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.945 | 10325 |
| 2026-09-05T11:20:08.9790202Z | 2026-09-05T11:20:39.4627872Z | Building LLD for aarch64-pc-windows-msvc | 0.508 | 10447 |
| 2026-09-05T11:20:39.4639943Z | 2026-09-05T11:20:41.6824692Z | Building stage1 lld-wrapper (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.037 | 10688 |
| 2026-09-05T11:20:41.6921779Z | 2026-09-05T11:21:46.1562575Z | Building stage1 wasm-component-ld (stage0 -> stage1, aarch64-pc-windows-msvc) | 1.074 | 10697 |
| 2026-09-05T11:21:46.1592957Z | 2026-09-05T11:22:00.8046895Z | Building stage1 llvm-bitcode-linker (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.244 | 10847 |
| 2026-09-05T11:22:00.8118707Z | 2026-09-05T11:23:23.7637736Z | Building stage1 library artifacts (stage1 -> stage1, aarch64-pc-windows-msvc) | 1.383 | 10928 |
| 2026-09-05T11:23:23.7654582Z | 2026-09-05T11:42:31.9398358Z | Building stage2 compiler artifacts (stage1 -> stage2, aarch64-pc-windows-msvc) | 19.136 | 10984 |
| 2026-09-05T11:42:31.9450721Z | 2026-09-05T11:45:59.2897537Z | Building stage2 codegen backend cranelift (stage1 -> stage2, aarch64-pc-windows-msvc) | 3.456 | 11588 |
| 2026-09-05T11:45:59.2934682Z | 2026-09-05T11:46:00.7320156Z | Building stage2 lld-wrapper (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.024 | 11682 |
| 2026-09-05T11:46:00.7430400Z | 2026-09-05T11:47:54.4125105Z | Building stage2 wasm-component-ld (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.894 | 11691 |
| 2026-09-05T11:47:54.4155519Z | 2026-09-05T11:48:17.2540693Z | Building stage2 llvm-bitcode-linker (stage1 -> stage2, aarch64-pc-windows-msvc) | 0.381 | 11820 |
| 2026-09-05T11:48:17.2929171Z | 2026-09-05T11:48:50.2298012Z | Building stage1 compiletest (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.549 | 11907 |
| 2026-09-05T11:48:50.2596524Z | 2026-09-05T11:48:50.3739911Z | Building test helpers for aarch64-pc-windows-msvc | 0.002 | 12091 |
| 2026-09-05T11:48:50.3993889Z | 2026-09-05T12:08:56.8986619Z | Testing stage2 with compiletest suite=ui mode=ui (aarch64-pc-windows-msvc) | 20.108 | 12095 |
| 2026-09-05T12:08:56.9372559Z | 2026-09-05T12:09:03.6038827Z | Testing stage2 with compiletest suite=crashes mode=crashes (aarch64-pc-windows-msvc) | 0.111 | 34283 |
| 2026-09-05T12:09:03.6318850Z | 2026-09-05T12:09:09.8120508Z | Building stage1 coverage-dump (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.103 | 34498 |
| 2026-09-05T12:09:09.8131676Z | 2026-09-05T12:09:16.5174106Z | Testing stage2 with compiletest suite=coverage mode=coverage-map (aarch64-pc-windows-msvc) | 0.112 | 34544 |
| 2026-09-05T12:09:16.5497915Z | 2026-09-05T12:09:16.7745094Z | Testing stage2 with compiletest suite=coverage mode=coverage-run (aarch64-pc-windows-msvc) | 0.004 | 34660 |
| 2026-09-05T12:09:16.7998812Z | 2026-09-05T12:09:50.4014624Z | Testing stage2 with compiletest suite=mir-opt mode=mir-opt (aarch64-pc-windows-msvc) | 0.560 | 34781 |
| 2026-09-05T12:09:50.4457041Z | 2026-09-05T12:10:48.2152621Z | Testing stage2 with compiletest suite=codegen-llvm mode=codegen (aarch64-pc-windows-msvc) | 0.963 | 35202 |
| 2026-09-05T12:10:48.2453108Z | 2026-09-05T12:10:50.8384716Z | Testing stage2 with compiletest suite=codegen-units mode=codegen-units (aarch64-pc-windows-msvc) | 0.043 | 36430 |
| 2026-09-05T12:10:50.8695836Z | 2026-09-05T12:11:44.4746139Z | Testing stage2 with compiletest suite=assembly-llvm mode=assembly (aarch64-pc-windows-msvc) | 0.893 | 36487 |
| 2026-09-05T12:11:44.5081629Z | 2026-09-05T12:12:24.3824302Z | Testing stage2 with compiletest suite=incremental mode=incremental (aarch64-pc-windows-msvc) | 0.665 | 37272 |
| 2026-09-05T12:12:26.6000147Z | 2026-09-05T12:13:05.9558817Z | Testing stage2 with compiletest suite=debuginfo mode=debuginfo (aarch64-pc-windows-msvc) | 0.656 | 37465 |
| 2026-09-05T12:13:06.2037623Z | 2026-09-05T12:13:43.8604411Z | Testing stage2 with compiletest suite=ui-fulldeps mode=ui (aarch64-pc-windows-msvc) | 0.628 | 38000 |
| 2026-09-05T12:13:43.8962624Z | 2026-09-05T12:16:39.1260466Z | Building stage2 rustdoc-tool-binary (stage1 -> stage2, aarch64-pc-windows-msvc) | 2.920 | 38091 |
| 2026-09-05T12:16:39.1286096Z | 2026-09-05T12:18:54.7556614Z | Testing stage2 with compiletest suite=rustdoc-html mode=rustdoc-html (aarch64-pc-windows-msvc) | 2.260 | 38298 |
| 2026-09-05T12:18:54.7907419Z | 2026-09-05T12:18:55.0106794Z | Testing stage2 with compiletest suite=coverage-run-rustdoc mode=coverage-run (aarch64-pc-windows-msvc) | 0.004 | 39112 |
| 2026-09-05T12:18:55.0419188Z | 2026-09-05T12:19:00.2678411Z | Testing stage2 with compiletest suite=pretty mode=pretty (aarch64-pc-windows-msvc) | 0.087 | 39126 |
| 2026-09-05T12:19:00.3155622Z | 2026-09-05T12:31:01.2235476Z | Testing stage2 {alloc, alloctests, compiler_builtins, core, coretests, panic_abort, panic_unwind, proc_macro, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} (aarch64-pc-windows-msvc) | 12.015 | 39257 |
| 2026-09-05T12:31:01.2292033Z | 2026-09-05T12:32:00.9941619Z | Testing stage1 tidy (aarch64-pc-windows-msvc) | 0.996 | 55304 |
| 2026-09-05T12:32:00.9991313Z | 2026-09-05T12:33:37.8365745Z | Building stage2 error_index_generator (stage1 -> stage2, aarch64-pc-windows-msvc) | 1.614 | 55613 |
| 2026-09-05T12:33:37.8382858Z | 2026-09-05T12:33:37.9334078Z | Testing stage2 error-index (aarch64-pc-windows-msvc) | 0.002 | 55896 |
| 2026-09-05T12:34:51.3064582Z | 2026-09-05T12:35:47.2837350Z | Testing stage1 stdarch-verify (aarch64-pc-windows-msvc) | 0.933 | 57026 |
| 2026-09-05T12:35:47.2910309Z | 2026-09-05T12:38:24.4604911Z | Documenting stage2 library{alloc, compiler_builtins, core, panic_abort, panic_unwind, proc_macro, rustc-std-workspace-core, std, std_detect, sysroot, test, unwind} in HTML format (stage2 -> stage2, aarch64-pc-windows-msvc) | 2.619 | 57111 |
| 2026-09-05T12:38:24.4616318Z | 2026-09-05T12:39:11.5257438Z | Testing stage2 rustdoc-js-std (aarch64-pc-windows-msvc) | 0.784 | 57165 |
| 2026-09-05T12:39:11.5865760Z | 2026-09-05T12:39:36.4255044Z | Testing stage2 with compiletest suite=rustdoc-js mode=rustdoc-js (aarch64-pc-windows-msvc) | 0.414 | 57237 |
| 2026-09-05T12:39:36.4768570Z | 2026-09-05T12:40:11.0711762Z | Testing stage2 with compiletest suite=rustdoc-ui mode=ui (aarch64-pc-windows-msvc) | 0.577 | 57328 |
| 2026-09-05T12:40:11.1208421Z | 2026-09-05T12:40:34.9880887Z | Building stage1 jsondocck (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.398 | 57787 |
| 2026-09-05T12:40:34.9895585Z | 2026-09-05T12:40:48.5761159Z | Building stage1 jsondoclint (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.226 | 57921 |
| 2026-09-05T12:40:48.5771132Z | 2026-09-05T12:41:03.4670309Z | Testing stage2 with compiletest suite=rustdoc-json mode=rustdoc-json (aarch64-pc-windows-msvc) | 0.248 | 57975 |
| 2026-09-05T12:41:03.5239362Z | 2026-09-05T12:41:16.2704885Z | Building stage1 run_make_support (stage0 -> stage1, aarch64-pc-windows-msvc) | 0.212 | 58182 |
| 2026-09-05T12:41:16.2722008Z | 2026-09-05T12:45:06.9994147Z | Testing stage2 with compiletest suite=run-make mode=run-make (aarch64-pc-windows-msvc) | 3.845 | 58265 |
| 2026-09-05T12:45:07.0708677Z | 2026-09-05T12:54:11.4110085Z | Building stage2 cargo (stage1 -> stage2, aarch64-pc-windows-msvc) | 9.072 | 58799 |
| 2026-09-05T12:54:11.4143621Z | 2026-09-05T12:57:56.5285416Z | Testing stage2 with compiletest suite=run-make-cargo mode=run-make (aarch64-pc-windows-msvc) | 3.752 | 59735 |

</details>
