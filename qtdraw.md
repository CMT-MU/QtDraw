# MultiPie 機能 (add QtDraw.app only)

- Group
    - group : group (space/point)

- Object Drawing
    - site : site
    - bond : bond
    - vector : type, vector # site/bond
    - orbital : type, orbital # site/bond
    - harmonics : type, rank, irrep, site/bond

- Basis Drawing (objectを返してplotできるようにするほうがよいかも)
    - site : site, basis_tag
    - bond : bond, basis_tag
    - vector : type, site/bond, basis_tag
    - vector_lc : type, site/bond, lc_exp
    - vector_modulation : type, site/bond, [basis_tag, coeff, k_vector, cos/sin]
    - orbital : type, rank, site/bond, basis_tag
    - orbital_lc : type, rank, site/bond, lc_exp
    - orbital_modulation : type, rank, site/bond, [basis_tag, coeff, k_vector, cos/sin]
    - hopping : bond
