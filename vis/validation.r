###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)
library(kableExtra)
library(magick)

cb <- function(x) {
  range <- max(abs(x))
  width <- round(abs(x / range * 50), 2)
  ifelse(
    x > 0,
    paste0(
      '<span style="display: inline-block; border-radius: 2px; ',
      'padding-right: 2px; background-color: lightpink; width: ',
      width, '%; margin-left: 50%; text-align: left;">', x, '</span>'
    ),
    paste0(
      '<span style="display: inline-block; border-radius: 2px; ',
      'padding-right: 2px; background-color: lightgreen; width: ',
      width, '%; margin-right: 50%; text-align: right; float: right; ">', 
      x, '</span>'
    )
  )
}

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'user_costs', 'decile_cost_estimates.csv'))

data <- data[(data$confidence == 50),]

data = data[!grepl("psb", data$strategy),]
data = data[!grepl("moran", data$strategy),]
data = data[!grepl("srn", data$strategy),]

data$scenario_adopt = ''
data$scenario_adopt[grep("high", data$scenario)] = 'High Adoption'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline Adoption'
data$scenario_adopt[grep("low", data$scenario)] = 'Low Adoption'
data$scenario_adopt = factor(data$scenario_adopt,
                             levels=c("Low Adoption",
                                      "Baseline Adoption",
                                      "High Adoption"))

data$scenario_capacity = ''
data$scenario_capacity[grep("10_10_10", data$scenario)] = '10'
data$scenario_capacity[grep("20_20_20", data$scenario)] = '20'
data$scenario_capacity[grep("30_30_30", data$scenario)] = '30'

data <- data[(data$scenario_adopt == 'Baseline Adoption'),]
data <- data[(data$strategy == '4G_epc_wireless_baseline_baseline_baseline_baseline'),]
data <- data[(!data$scenario_capacity == '20'),]
data <- data[(data$input_cost == 'baseline'),]
data <- data[(data$confidence == 50),]

data$pop_km2 = data$population / data$area_km2

data = select(data, scenario_capacity, decile, population, area_km2, pop_km2, total_private_cost,
              total_government_cost, total_financial_cost)

names(data)[names(data)=="scenario_capacity"] <- "(GB/Month)"
names(data)[names(data)=="population"] <- "(Mn)"
names(data)[names(data)=="area_km2"] <- "(km^2)"
names(data)[names(data)=="pop_km2"] <- "(Pop/km^2)"
names(data)[names(data)=="total_private_cost"] <- "Private"
names(data)[names(data)=="total_government_cost"] <- "Govt"
names(data)[names(data)=="total_financial_cost"] <- "Financial"

data$`(Mn)` = round(data$`(Mn)` / 1e6, 0)
data$`(km^2)` = round(data$`(km^2)` / 1e6, 1)
data$`(Pop/km^2)` = round(data$`(Pop/km^2)`, 0)
data$`Private` = round(data$`Private`,0)
data$`Govt` = round(data$`Govt`,0)
data$`Financial` = round(data$`Financial`,0)

data$decile = factor(data$decile, levels=c("<20",
                                           "20-43",
                                           "43-69",
                                           "69-109",
                                           "109-171",
                                           "171-257",
                                           "257-367",
                                           "367-541",
                                           "541-1104",
                                           ">1104"
),
labels=c(
  "<20",
  "20-43",
  "43-69",
  "69-109",
  "109-171",
  "171-257",
  "257-367",
  "367-541",
  "541-1104",
  ">1104"
))

data = with(data, data[order(decile,decreasing = TRUE),])

row.names(data) <- NULL

sample <- data[(data$`(GB/Month)` == '30'),]
rownames(sample) <- NULL

tbl_1 = sample %>%
    mutate(
      `(Mn)` = cb(`(Mn)`),
      `(km^2)` = cb(`(km^2)`),
      `(Pop/km^2)` = cb(`(Pop/km^2)`),
      `Private` = cb(`Private`),
      `Govt` = cb(`Govt`),
      `Financial` = cb(`Financial`)
    ) %>%
    kable(escape = F, 
          caption = 'Cost Results by Decile for the Continent of Africa for 30 GB/Month Per User',
          align='l') %>%
    kable_classic("striped", full_width = F, html_font = "Cambria") %>%
    row_spec(0, align = "c")  %>%
    add_header_above(
      c("Capacity"= 1,"Pop. D."=1,"Pop."=1,"Area"=1,"Pop. D."=1, "Cost Type ($Bn)" = 3)) 

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures')
setwd(path)
kableExtra::save_kable(tbl_1, file='validation_30gb.png', zoom = 1)

path = file.path(folder, 'figures')
write.csv(sample, 'costs_by_decile_30gb.csv')

#######################

sample <- data[(data$`(GB/Month)` == '10'),]
rownames(sample) <- NULL

tbl_2 =
  sample %>%
  mutate(
    `(Mn)` = cb(`(Mn)`),
    `(km^2)` = cb(`(km^2)`),
    `(Pop/km^2)` = cb(`(Pop/km^2)`),
    `Private` = cb(`Private`),
    `Govt` = cb(`Govt`),
    `Financial` = cb(`Financial`)
  ) %>%
  kable(escape = F,
        caption = 'Cost Results by Decile for the Continent of Africa for 10 GB/Month Per User',
        align='l') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c")  %>%
  add_header_above(
    c("Capacity"= 1,"Pop. D."=1,"Pop."=1,"Area"=1,"Pop. D."=1, "Cost Type ($Bn)" = 3))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures')
setwd(path)
kableExtra::save_kable(tbl_2, file='validation_10gb.png', zoom = 1)

path = file.path(folder, 'figures')
write.csv(data, 'costs_by_decile_10gb.csv')

# # library(png)
# # img1 <- readPNG(file.path(folder, 'figures', 'validation_10_mbps.png'))
# # img2 <- readPNG(file.path(folder, 'figures', 'validation_2_mbps.png'))
# # 
# # # library(gridExtra)    
# # # grid.arrange(img1, img2, ncol=1, nrow=2)
# # 
# # plot_list <- map(c(img1, ),myplot)
# # 
# # ggarrange(plotlist = plot_list,
# #           labels = c("A", "B"),
# #           ncol = 1, nrow = 2)
