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

data <- read.csv(file.path(folder, '..', 'results', 'user_costs', 'decile_cost_estimates_10.csv'))
data = data[(data$Strategy == '4G(W)' & data$Scenario == 'Baseline'),]
data$Capacity = '~10'

data$pop_km2 = data$Population...10.Years. / data$Area..Km2.

data = select(data, Capacity, Decile, Population...10.Years., Area..Km2., pop_km2, Private.Cost...Bn.,
              Government.Cost...Bn., Financial.Cost...Bn.)

names(data)[names(data)=="Capacity"] <- "(Mbps)"
names(data)[names(data)=="Population...10.Years."] <- "(Mn)"
names(data)[names(data)=="Area..Km2."] <- "(km^2)"
names(data)[names(data)=="pop_km2"] <- "(Pop/km^2)"
names(data)[names(data)=="Private.Cost...Bn."] <- "Private"
names(data)[names(data)=="Government.Cost...Bn."] <- "Govt"
names(data)[names(data)=="Financial.Cost...Bn."] <- "Financial"

data$`(Mn)` = round(data$`(Mn)` / 1e6, 0)
data$`(km^2)` = round(data$`(km^2)` / 1e6, 1)
data$`(Pop/km^2)` = round(data$`(Pop/km^2)`, 0)
data$`Private` = round(data$`Private`,0)
data$`Govt` = round(data$`Govt`,0)
data$`Financial` = round(data$`Financial`,0)

data$Decile = factor(data$Decile, levels=c("<20",
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

data = with(data, data[order(Decile,decreasing = TRUE),])

row.names(data) <- NULL

tbl_1 = data %>%
    mutate(
      `(Mn)` = cb(`(Mn)`),
      `(km^2)` = cb(`(km^2)`),
      `(Pop/km^2)` = cb(`(Pop/km^2)`),
      `Private` = cb(`Private`),
      `Govt` = cb(`Govt`),
      `Financial` = cb(`Financial`)
    ) %>%
    kable(escape = F, 
          caption = '(A) Cost Results by Decile for the Continent of Africa for ~10 Mbps Per User',
          align='l') %>%
    kable_classic("striped", full_width = F, html_font = "Cambria") %>%
    row_spec(0, align = "c")  %>%
    add_header_above(
      c("Capacity"= 1,"Pop. D."=1,"Pop."=1,"Area"=1,"Pop. D."=1, "Cost Type ($Bn)" = 3)) 

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures')
setwd(path)
kableExtra::save_kable(tbl_1, file='validation_10_mbps.png', zoom = 1)

path = file.path(folder, 'figures')
write.csv(data, 'costs_by_decile_10_mbps.csv')

#######################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'user_costs', 'decile_cost_estimates_2.csv'))
data = data[(data$Strategy == '4G(W)' & data$Scenario == 'Baseline'),]
data$Capacity = '~2'

data$pop_km2 = data$Population...10.Years. / data$Area..Km2.

data = select(data, Capacity, Decile, Population...10.Years., Area..Km2., pop_km2, Private.Cost...Bn.,
              Government.Cost...Bn., Financial.Cost...Bn.)

names(data)[names(data)=="Capacity"] <- "(Mbps)"
names(data)[names(data)=="Population...10.Years."] <- "(Mn)"
names(data)[names(data)=="Area..Km2."] <- "(km^2)"
names(data)[names(data)=="pop_km2"] <- "(Pop/km^2)"
names(data)[names(data)=="Private.Cost...Bn."] <- "Private"
names(data)[names(data)=="Government.Cost...Bn."] <- "Govt"
names(data)[names(data)=="Financial.Cost...Bn."] <- "Financial"

data$`(Mn)` = round(data$`(Mn)` / 1e6, 0)
data$`(km^2)` = round(data$`(km^2)` / 1e6, 1)
data$`(Pop/km^2)` = round(data$`(Pop/km^2)`, 0)
data$`Private` = round(data$`Private`,0)
data$`Govt` = round(data$`Govt`,0)
data$`Financial` = round(data$`Financial`,0)

data$Decile = factor(data$Decile, levels=c("<20",
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

data = with(data, data[order(Decile,decreasing = TRUE),])

row.names(data) <- NULL

tbl_2 = data %>%
  mutate(
    `(Mn)` = cb(`(Mn)`),
    `(km^2)` = cb(`(km^2)`),
    `(Pop/km^2)` = cb(`(Pop/km^2)`),
    `Private` = cb(`Private`),
    `Govt` = cb(`Govt`),
    `Financial` = cb(`Financial`)
  ) %>%
  kable(escape = F, 
        caption = '(B) Cost Results by Decile for the Continent of Africa for ~2 Mbps Per User',
        align='l') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c")  %>%
  add_header_above(
    c("Capacity"= 1,"Pop. D."=1,"Pop."=1,"Area"=1,"Pop. D."=1, "Cost Type ($Bn)" = 3)) 

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures')
setwd(path)
kableExtra::save_kable(tbl_2, file='validation_2_mbps.png', zoom = 1)

path = file.path(folder, 'figures')
write.csv(data, 'costs_by_decile_2_mbps.csv')

# library(png)
# img1 <- readPNG(file.path(folder, 'figures', 'validation_10_mbps.png'))
# img2 <- readPNG(file.path(folder, 'figures', 'validation_2_mbps.png'))
# 
# # library(gridExtra)    
# # grid.arrange(img1, img2, ncol=1, nrow=2)
# 
# plot_list <- map(c(img1, ),myplot)
# 
# ggarrange(plotlist = plot_list,
#           labels = c("A", "B"),
#           ncol = 1, nrow = 2)
