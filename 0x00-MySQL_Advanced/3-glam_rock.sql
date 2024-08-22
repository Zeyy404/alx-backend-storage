-- lists all bands with Glam rock as their main style
--  ranked by their longevity
SELECT
    band_name,
    CASE
        WHEN split_year IS NOT NULL THEN split_year - formed_year
        ELSE 2022 - formed_year
    END AS lifespan
FROM
    metal_bands
WHERE
    main_style = 'Glam rock'
ORDER BY
    lifespan DESC;
