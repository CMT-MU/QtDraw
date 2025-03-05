"""
Default setting for MultiPie plugin.
"""

# ==================================================
default_status = {
    "group": {
        "group": "Oh",
        #
        "irrep1": "A1g",
        "irrep2": "A1g",
        "irrep": "A1g",
        #
        "harmonics_type": "Q",
        "harmonics_rank": 0,
        "harmonics_decomp": "C1",
        #
        "response_type": "Q",
        "response_rank": 1,
        #
        "atomic_type": "Q",
        "atomic_basis_type": "jm",
        "atomic_bra": "(5/2,3)",
        "atomic_ket": "(5/2,3)",
        #
        "vc_wyckoff": "48f",
        "vc_neighbor": "[1]",
    },
    "object": {
        "site": "[1/2, 1/2, 0]",  # position.
        #
        "bond": "[0, 0, 0] ; [1/2, 1/2, 0]",  # position.
        #
        "vector_type": "Q",  # type.
        "vector": "[0, 0, 1] # [1/2, 1/2, 0]",  # v # position.
        #
        "orbital_type": "Q",  # type.
        "orbital": "3z**2 - r**2 # [1/4, 1/4, 0]",  # orbital # position.
        #
        "harmonics_type": "Q",  #  type.
        "harmonics_rank": 0,  #  rank.
        "harmonics_irrep": 0,  # irrep id.
        "harmonics": "[0, 0, 0]",  # position.
        "harmonics_latex": False,  # LaTeX ?
        #
        "wyckoff": "[0, 0, 0]",  #  position.
    },
    "basis": {
        "site": "[1/2, 1/2, 0]",  #  position.
        #
        "bond": "[1/2, 1/2, 0] @ [1/4, 1/4, 0]",  # position.
        #
        "vector_type": "Q",  # vector type.
        "vector": "[1/2, 1/2, 0]",  # position.
        "vector_samb_type": "Q",  # vector samb type.
        "vector_lc": "",  #  expression of linear combination.
        "vector_modulation_type": "Q,G",  # type.
        "vector_modulation": "",  # modulation str.
        #
        "orbital_type": "Q",  # orbital type.
        "orbital_rank": 1,  # orbital rank.
        "orbital": "[0, 0, 0] ; [1/2, 1/2, 0]",  # position.
        "orbital_samb_type": "Q",  # samb type.
        "orbital_lc": "",  #  expression of linear combination.
        "orbital_modulation_type": "Q,G",  # type.
        "orbital_modulation": "",  # modulation str.
        #
        "hopping": "[0, 0, 0] ; [1/2, 1/2, 0]",  # hopping.
    },
    "counter": {
        "site": 0,
        "bond": 0,
        "vector": 0,
        "orbital": 0,
        #
        "site_samb": 0,
        "bond_samb": 0,
        "vector_samb": 0,
        "orbital_samb": 0,
        "hopping": 0,
    },
}

# ==================================================
plugin_detail = {
    "general": {
        "label": False,  # show label ?
        "site_color": "darkseagreen",
        "bond_color1": "silver",
        "bond_color2": "iron",
        "vector_color_Q": "orange",
        "vector_color_M": "lightskyblue",
        "vector_color_T": "hotpink",
        "vector_color_G": "yellowgreen",
        "orbital_color_Q": "Wistia",
        "orbital_color_M": "GnBu",
        "orbital_color_T": "coolwarm",
        "orbital_color_G": "PiYG",
    },
    "site": [  # (color, size, opacity)
        ("darkseagreen", 1.0, 1.0),  # 1st site
        ("lightblue", 1.0, 1.0),  # 2nd site
        ("sandybrown", 1.0, 1.0),  # 9th site
        ("gold", 1.0, 1.0),  # 3rd site
        ("darkkhaki", 1.0, 1.0),  # 4th site
        ("skyblue", 1.0, 1.0),  # 7th site
        ("thistle", 1.0, 1.0),  # 6th site
        ("darkgrey", 1.0, 1.0),  # 8th site
        ("burlywood", 1.0, 1.0),  # 5th site
        ("ghostwhite", 1.0, 1.0),  # other sites
    ],
    "bond": [  # ((tail-color, head-color), width, opacity)
        (("snow", "silver"), 1.0, 1.0),  # 1st neighbor
        (("lightcyan", "lightsteelblue"), 1.0, 1.0),  # 2nd neighbor
        (("antiquewhite", "burlywood"), 1.0, 1.0),  # 3rd neighbor
        (("palegoldenrod", "darkseagreen"), 1.0, 1.0),  # 4th neighbor
        (("mistyrose", "lightpink"), 1.0, 1.0),  # 5th neighbor
        (("aliceblue", "lightblue"), 1.0, 1.0),  # 6th neighbor
        (("wheat", "sandybrown"), 1.0, 1.0),  # 7th neighbor
        (("seashell", "thistle"), 1.0, 1.0),  # 8th neighbor
        (("cornsilk", "peachpuff"), 1.0, 1.0),  # 9th neighbor
        (("whitesmoke", "darkkhaki"), 1.0, 1.0),  # other neighbors
    ],
    "object": {
        "site_size": 0.05,
        "bond_width": 0.01,
        "vector_length": 0.3,
        "orbital_size": 0.2,
    },
    "samb": {
        "site_size": 0.05,
        "site_scale": 0.7,
        "bond_width": 0.03,
        "bond_scale": 0.7,
        "vector_width": 0.02,
        "orbital_size": -0.2,
        "orbital_mod": -0.2,
    },
    "group": {"harmonics_size": 0.3},
}

# ==================================================
modulation_panel = {
    "id": ("hide", None, "0"),
    "basis": ("combo", ["Q01"], "Q01"),
    "coeff": ("sympy", [""], "1"),
    "k_vector": ("list", ((3,), [""], 3), "[1,0,0]"),
    "phase": ("combo", (["cos", "sin"]), "cos"),
}


# ==================================================
# crylsta list.
crystal_list = ["triclinic", "monoclinic", "orthorhombic", "tetragonal", "trigonal", "hexagonal", "cubic"]

# ==================================================
# space group list.
space_group_list = {
    "triclinic": ["1. C1^1 (P1)", "2. Ci^1 (P-1)"],
    "monoclinic": [
        "3. C2^1 (P2)",
        "4. C2^2 (P2_1)",
        "5. C2^3 (C2)",
        "6. Cs^1 (Pm)",
        "7. Cs^2 (Pc)",
        "8. Cs^3 (Cm)",
        "9. Cs^4 (Cc)",
        "10. C2h^1 (P2/m)",
        "11. C2h^2 (P2_1/m)",
        "12. C2h^3 (C2/m)",
        "13. C2h^4 (P2/c)",
        "14. C2h^5 (P2_1/c)",
        "15. C2h^6 (C2/c)",
    ],
    "orthorhombic": [
        "16. D2^1 (P222)",
        "17. D2^2 (P222_1)",
        "18. D2^3 (P2_12_12)",
        "19. D2^4 (P2_12_12_1)",
        "20. D2^5 (C222_1)",
        "21. D2^6 (C222)",
        "22. D2^7 (F222)",
        "23. D2^8 (I222)",
        "24. D2^9 (I2_12_12_1)",
        "25. C2v^1 (Pmm2)",
        "26. C2v^2 (Pmc2_1)",
        "27. C2v^3 (Pcc2)",
        "28. C2v^4 (Pma2)",
        "29. C2v^5 (Pca2_1)",
        "30. C2v^6 (Pnc2)",
        "31. C2v^7 (Pmn2_1)",
        "32. C2v^8 (Pba2)",
        "33. C2v^9 (Pna2_1)",
        "34. C2v^10 (Pnn2)",
        "35. C2v^11 (Cmm2)",
        "36. C2v^12 (Cmc2_1)",
        "37. C2v^13 (Ccc2)",
        "38. C2v^14 (Amm2)",
        "39. C2v^15 (Aem2)",
        "40. C2v^16 (Ama2)",
        "41. C2v^17 (Aea2)",
        "42. C2v^18 (Fmm2)",
        "43. C2v^19 (Fdd2)",
        "44. C2v^20 (Imm2)",
        "45. C2v^21 (Iba2)",
        "46. C2v^22 (Ima2)",
        "47. D2h^1 (Pmmm)",
        "48. D2h^2 (Pnnn)",
        "49. D2h^3 (Pccm)",
        "50. D2h^4 (Pban)",
        "51. D2h^5 (Pmma)",
        "52. D2h^6 (Pnna)",
        "53. D2h^7 (Pmna)",
        "54. D2h^8 (Pcca)",
        "55. D2h^9 (Pbam)",
        "56. D2h^10 (Pccn)",
        "57. D2h^11 (Pbcm)",
        "58. D2h^12 (Pnnm)",
        "59. D2h^13 (Pmmn)",
        "60. D2h^14 (Pbcn)",
        "61. D2h^15 (Pbca)",
        "62. D2h^16 (Pnma)",
        "63. D2h^17 (Cmcm)",
        "64. D2h^18 (Cmce)",
        "65. D2h^19 (Cmmm)",
        "66. D2h^20 (Cccm)",
        "67. D2h^21 (Cmme)",
        "68. D2h^22 (Ccce)",
        "69. D2h^23 (Fmmm)",
        "70. D2h^24 (Fddd)",
        "71. D2h^25 (Immm)",
        "72. D2h^26 (Ibam)",
        "73. D2h^27 (Ibca)",
        "74. D2h^28 (Imma)",
    ],
    "tetragonal": [
        "75. C4^1 (P4)",
        "76. C4^2 (P4_1)",
        "77. C4^3 (P4_2)",
        "78. C4^4 (P4_3)",
        "79. C4^5 (I4)",
        "80. C4^6 (I4_1)",
        "81. S4^1 (P-4)",
        "82. S4^2 (I-4)",
        "83. C4h^1 (P4/m)",
        "84. C4h^2 (P4_2/m)",
        "85. C4h^3 (P4/n)",
        "86. C4h^4 (P4_2/n)",
        "87. C4h^5 (I4/m)",
        "88. C4h^6 (I4_1/a)",
        "89. D4^1 (P422)",
        "90. D4^2 (P42_12)",
        "91. D4^3 (P4_122)",
        "92. D4^4 (P4_12_12)",
        "93. D4^5 (P4_222)",
        "94. D4^6 (P4_22_12)",
        "95. D4^7 (P4_322)",
        "96. D4^8 (P4_32_12)",
        "97. D4^9 (I422)",
        "98. D4^10 (I4_122)",
        "99. C4v^1 (P4mm)",
        "100. C4v^2 (P4bm)",
        "101. C4v^3 (P4_2cm)",
        "102. C4v^4 (P4_2nm)",
        "103. C4v^5 (P4cc)",
        "104. C4v^6 (P4nc)",
        "105. C4v^7 (P4_2mc)",
        "106. C4v^8 (P4_2bc)",
        "107. C4v^9 (I4mm)",
        "108. C4v^10 (I4cm)",
        "109. C4v^11 (I4_1md)",
        "110. C4v^12 (I4_1cd)",
        "111. D2d^1 (P-42m)",
        "112. D2d^2 (P-42c)",
        "113. D2d^3 (P-42_1m)",
        "114. D2d^4 (P-42_1c)",
        "115. D2d^5 (P-4m2)",
        "116. D2d^6 (P-4c2)",
        "117. D2d^7 (P-4b2)",
        "118. D2d^8 (P-4n2)",
        "119. D2d^9 (I-4m2)",
        "120. D2d^10 (I-4c2)",
        "121. D2d^11 (I-42m)",
        "122. D2d^12 (I-42d)",
        "123. D4h^1 (P4/mmm)",
        "124. D4h^2 (P4/mcc)",
        "125. D4h^3 (P4/nbm)",
        "126. D4h^4 (P4/nnc)",
        "127. D4h^5 (P4/mbm)",
        "128. D4h^6 (P4/mnc)",
        "129. D4h^7 (P4/nmm)",
        "130. D4h^8 (P4/ncc)",
        "131. D4h^9 (P4_2/mmc)",
        "132. D4h^10 (P4_2/mcm)",
        "133. D4h^11 (P4_2/nbc)",
        "134. D4h^12 (P4_2/nnm)",
        "135. D4h^13 (P4_2/mbc)",
        "136. D4h^14 (P4_2/mnm)",
        "137. D4h^15 (P4_2/nmc)",
        "138. D4h^16 (P4_2/ncm)",
        "139. D4h^17 (I4/mmm)",
        "140. D4h^18 (I4/mcm)",
        "141. D4h^19 (I4_1/amd)",
        "142. D4h^20 (I4_1/acd)",
    ],
    "trigonal": [
        "143. C3^1 (P3)",
        "144. C3^2 (P3_1)",
        "145. C3^3 (P3_2)",
        "146. C3^4 (R3)",
        "147. C3i^1 (P-3)",
        "148. C3i^2 (R-3)",
        "149. D3^1 (P312)",
        "150. D3^2 (P321)",
        "151. D3^3 (P3_112)",
        "152. D3^4 (P3_121)",
        "153. D3^5 (P3_212)",
        "154. D3^6 (P3_221)",
        "155. D3^7 (R32)",
        "156. C3v^1 (P3m1)",
        "157. C3v^2 (P31m)",
        "158. C3v^3 (P3c1)",
        "159. C3v^4 (P31c)",
        "160. C3v^5 (R3m)",
        "161. C3v^6 (R3c)",
        "162. D3d^1 (P-31m)",
        "163. D3d^2 (P-31c)",
        "164. D3d^3 (P-3m1)",
        "165. D3d^4 (P-3c1)",
        "166. D3d^5 (R-3m)",
        "167. D3d^6 (R-3c)",
    ],
    "hexagonal": [
        "168. C6^1 (P6)",
        "169. C6^2 (P6_1)",
        "170. C6^3 (P6_5)",
        "171. C6^4 (P6_2)",
        "172. C6^5 (P6_4)",
        "173. C6^6 (P6_3)",
        "174. C3h^1 (P-6)",
        "175. C6h^1 (P6/m)",
        "176. C6h^2 (P6_3/m)",
        "177. D6^1 (P622)",
        "178. D6^2 (P6_122)",
        "179. D6^3 (P6_522)",
        "180. D6^4 (P6_222)",
        "181. D6^5 (P6_422)",
        "182. D6^6 (P6_322)",
        "183. C6v^1 (P6mm)",
        "184. C6v^2 (P6cc)",
        "185. C6v^3 (P6_3cm)",
        "186. C6v^4 (P6_3mc)",
        "187. D3h^1 (P-6m2)",
        "188. D3h^2 (P-6c2)",
        "189. D3h^3 (P-62m)",
        "190. D3h^4 (P-62c)",
        "191. D6h^1 (P6/mmm)",
        "192. D6h^2 (P6/mcc)",
        "193. D6h^3 (P6_3/mcm)",
        "194. D6h^4 (P6_3/mmc)",
    ],
    "cubic": [
        "195. T^1 (P23)",
        "196. T^2 (F23)",
        "197. T^3 (I23)",
        "198. T^4 (P2_13)",
        "199. T^5 (I2_13)",
        "200. Th^1 (Pm-3)",
        "201. Th^2 (Pn-3)",
        "202. Th^3 (Fm-3)",
        "203. Th^4 (Fd-3)",
        "204. Th^5 (Im-3)",
        "205. Th^6 (Pa-3)",
        "206. Th^7 (Ia-3)",
        "207. O^1 (P432)",
        "208. O^2 (P4_232)",
        "209. O^3 (F432)",
        "210. O^4 (F4_132)",
        "211. O^5 (I432)",
        "212. O^6 (P4_332)",
        "213. O^7 (P4_132)",
        "214. O^8 (I4_132)",
        "215. Td^1 (P-43m)",
        "216. Td^2 (F-43m)",
        "217. Td^3 (I-43m)",
        "218. Td^4 (P-43n)",
        "219. Td^5 (F-43c)",
        "220. Td^6 (I-43d)",
        "221. Oh^1 (Pm-3m)",
        "222. Oh^2 (Pn-3n)",
        "223. Oh^3 (Pm-3n)",
        "224. Oh^4 (Pn-3m)",
        "225. Oh^5 (Fm-3m)",
        "226. Oh^6 (Fm-3c)",
        "227. Oh^7 (Fd-3m)",
        "228. Oh^8 (Fd-3c)",
        "229. Oh^9 (Im-3m)",
        "230. Oh^10 (Ia-3d)",
    ],
}

# ==================================================
# point group list.
point_group_list = {
    "triclinic": ["1. C1 (1)", "2. Ci (-1)"],
    "monoclinic": ["3. C2 (2)", "4. Cs (m)", "5. C2h (2/m)"],
    "orthorhombic": ["6. D2 (222)", "7. C2v (mm2)", "8. D2h (mmm)"],
    "tetragonal": [
        "9. C4 (4)",
        "10. S4 (-4)",
        "11. C4h (4/m)",
        "12. D4 (422)",
        "13. C4v (4mm)",
        "14. D2d (-42m)",
        "14. D2d-1 (-4m2)",
        "15. D4h (4/mmm)",
    ],
    "trigonal": [
        "16. C3 (3)",
        "17. C3i (-3)",
        "18. D3 (312)",
        "18. D3-1 (321)",
        "19. C3v (3m1)",
        "19. C3v-1 (31m)",
        "20. D3d (-31m)",
        "20. D3d-1 (-3m1)",
    ],
    "hexagonal": [
        "21. C6 (6)",
        "22. C3h (-6)",
        "23. C6h (6/m)",
        "24. D6 (622)",
        "25. C6v (6mm)",
        "26. D3h (-6m2)",
        "26. D3h-1 (-62m)",
        "27. D6h (6/mmm)",
    ],
    "cubic": ["28. T (23)", "29. Th (m-3)", "30. O (432)", "31. Td (-43m)", "32. Oh (m-3m)"],
}

# ==================================================
# point group.
point_group_all_list = list(sum(point_group_list.values(), []))
