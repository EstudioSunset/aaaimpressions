module.exports = function (eleventyConfig) {
  // Images and fonts from existing root assets/
  eleventyConfig.addPassthroughCopy({ "assets/img": "assets/img" });
  eleventyConfig.addPassthroughCopy({ "assets/css": "assets/css" });

  // JS from src
  eleventyConfig.addPassthroughCopy("src/assets/js");

  // CNAME for custom domain on GitHub Pages
  eleventyConfig.addPassthroughCopy("CNAME");

  // Robots.txt — pass through as plain file, not template
  eleventyConfig.addPassthroughCopy("src/robots.txt");

  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      data: "_data",
    },
    templateFormats: ["njk", "html", "md"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
  };
};
