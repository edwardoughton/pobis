library(tidyverse)
# library(ggpubr)
library(kableExtra)
library(magick)

###################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
data <- read.csv(file.path(folder, '..', 'results', 'model_results', 
               'national_market_cost_results_technology_options.csv'))

data <- data[(data$confidence == 50),]

names(data)[names(data) == 'GID_0'] <- 'country'

data <- select(data, scenario, strategy, country, social_cost)

data = filter(data, scenario %in% 
                c('low_10_10_10', 'baseline_10_10_10', 'high_10_10_10'))

data$strategy = factor(data$strategy, levels=c(
  "3G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
  "3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
  "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
  "4G_epc_fiber_baseline_baseline_baseline_baseline_baseline"),
  labels=c("3G (W)",
           "3G (FB)",
           "4G (W)",
           "4G (FB)"))

data = data[!duplicated(data[c('scenario', 'country', 'strategy')]),]

data$scenario = factor(data$scenario, levels=c("high_10_10_10", 
                                               "baseline_10_10_10",
                                               "low_10_10_10"),
                           labels=c("High (~10 Mbps)",
                                    "Baseline (~10 Mbps)",
                                    "Low (~10 Mbps)"))

data$social_cost = round(data$social_cost / 1e9, 0)

names(data)[names(data) == 'scenario'] <- 'Scenario'
names(data)[names(data) == 'strategy'] <- 'Strategy'

data <- spread(data, country, social_cost)

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
      width, '%; margin-right: 50%; text-align: right; float: right; ">', x, '</span>'
    )
  )
}

table6 = data %>%
  mutate(
    CIV = cb(CIV),
    MLI = cb(MLI),
    SEN = cb(SEN),
    KEN = cb(KEN),
    TZA = cb(TZA),
    UGA = cb(UGA),
  ) %>%
  kable(escape = F, caption = '(A) Social Cost of Universal Access NPV 2020-2030 by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" "= 2, "Social Cost (USD Billions)" = 6))  %>%
  footnote(number = c("Results rounded to the nearest whole number"))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures_tables')
dir.create(path, showWarnings = FALSE)
setwd(path)
kableExtra::save_kable(table6, file='f_a_social_cost.png', zoom = 1.5)

###################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
data_revenue <- read.csv(file.path(folder, '..', 'results', 'model_results', 'national_mno_results_technology_options.csv'))
data_revenue <- data_revenue[(data_revenue$confidence == 50),]
data_revenue <- select(data_revenue, GID_0, scenario, strategy, total_mno_revenue)

data <- read.csv(file.path(folder, '..', 'results', 'model_results', 'decile_mno_cost_results_technology_options.csv'))
data <- data[(data$confidence == 50),]
data = filter(data, scenario %in% 
                c('low_10_10_10', 'baseline_10_10_10', 'high_10_10_10'))

data <- select(data, GID_0, scenario, strategy, decile, total_mno_cost, required_state_subsidy)

data <- merge(data, data_revenue, by=c('GID_0', 'strategy', 'scenario'))

data <- data[order(data$GID_0, data$scenario, data$strategy, data$decile),]

data <- data %>%
  group_by(GID_0, scenario, strategy) %>%
  mutate(
    total_mno_revenue = total_mno_revenue/1e9,
    cumulative_cost_bn = cumsum(round(total_mno_cost / 1e9, 3)),
    cumulative_subsidy_bn = cumsum(round(required_state_subsidy / 1e9, 2))
  )

data <- data %>%
  group_by(GID_0, strategy, scenario) %>%
  filter(total_mno_revenue >= cumulative_cost_bn)

subsidy_all = data

data <- data %>%
  group_by(GID_0, scenario, strategy) %>%
  filter(decile == max(decile)) 

data$strategy = factor(data$strategy, levels=c(
  "3G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
  "3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
  "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
  "4G_epc_fiber_baseline_baseline_baseline_baseline_baseline"),
  labels=c("3G (W)",
           "3G (FB)",
           "4G (W)",
           "4G (FB)"))

data$scenario = factor(data$scenario, levels=c("high_10_10_10", 
                                               "baseline_10_10_10",
                                               "low_10_10_10"),
                       labels=c("High (~10 Mbps)",
                                "Baseline (~10 Mbps)",
                                "Low (~10 Mbps)"))

data = select(data, scenario, GID_0, decile, strategy)

data = data[!duplicated(data[c('scenario', 'GID_0', 'strategy')]),]

names(data)[names(data) == 'scenario'] <- 'Scenario'
names(data)[names(data) == 'strategy'] <- 'Strategy'

data <- spread(data, GID_0, decile)

data[is.na(data)] <- 0

cb_inverted <- function(x) {
  range <- max(abs(x))
  width <- round(abs(range / x * 5), 2)
  ifelse(
    x < 100,
    paste0(
      '<span style="display: inline-block; border-radius: 2px; ',
      'padding-right: 2px; background-color: lightpink; width: ',
      width, '%; margin-right: 50%; text-align: right; float: right; ">', x, '</span>'
    ),
    paste0(
      '<span style="display: inline-block; border-radius: 2px; ',
      'padding-right: 2px; background-color: lightgreen; width: ',
      width, '%; margin-left: 50%; text-align: left;">', x, '</span>'
    )
    
  )
}

table7 = data %>%
  mutate(
    CIV = cb_inverted(CIV),
    MLI = cb_inverted(MLI),
    SEN = cb_inverted(SEN),
    KEN = cb_inverted(KEN),
    TZA = cb_inverted(TZA),
    UGA = cb_inverted(UGA),
  ) %>%
  kable(escape = F, caption = '(B) Commercially Viable Population Coverage by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" "= 2, "Max Population Coverage (%)" = 6))  %>%
  footnote(number = c("Results rounded to the nearest whole number"))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures_tables')
setwd(path)
kableExtra::save_kable(table7, file='f_b_viable_coverage.png', zoom = 1.5)

# #########################################
# subsidy = ungroup(subsidy_all)
# 
# subsidy <- subsidy %>%
#   group_by(GID_0, scenario, strategy) %>%
#   filter(decile == max(decile)) 
# 
# subsidy = select(subsidy, scenario, strategy, GID_0, cumulative_subsidy_bn)
# 
# subsidy = subsidy[!duplicated(subsidy[c('scenario', 'GID_0', 'strategy')]),]
# 
# subsidy$strategy = factor(subsidy$strategy, levels=c(
#                   "3G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
#                   "3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
#                   "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
#                   "4G_epc_fiber_baseline_baseline_baseline_baseline_baseline"),
#                   labels=c("3G (W)",
#                            "3G (FB)",
#                            "4G (W)",
#                            "4G (FB)"))
# 
# subsidy$scenario = factor(subsidy$scenario, levels=c("high_10_10_10", 
#                                                "baseline_10_10_10",
#                                                "low_10_10_10"),
#                        labels=c("High (~10 Mbps)",
#                                 "Baseline (~10 Mbps)",
#                                 "Low (~10 Mbps)"))
# 
# names(subsidy)[names(subsidy) == 'scenario'] <- 'Scenario'
# names(subsidy)[names(subsidy) == 'strategy'] <- 'Strategy'
# 
# subsidy
# 
# subsidy <- spread(subsidy, GID_0, cumulative_subsidy_bn)
# 
# table8 = subsidy %>%
#   mutate(
#     CIV = cb(CIV),
#     MLI = cb(MLI),
#     SEN = cb(SEN),
#     KEN = cb(KEN),
#     TZA = cb(TZA),
#     UGA = cb(UGA),
#   ) %>%
#   kable(escape = F, 
#         caption = '(C) Govt. Subsidy to Reach Universal Access NPV 2020-2030 by Country') %>%
#   kable_classic("striped", full_width = F, html_font = "Cambria") %>%
#   row_spec(0, align = "c") %>%
#   add_header_above(
#     c(" "= 2, "Required Govt. Subsidy (USD Billions)" = 6))  %>%
#   footnote(number = c("Results rounded to the nearest whole number"))
# 
# folder <- dirname(rstudioapi::getSourceEditorContext()$path)
# path = file.path(folder, 'figures_tables')
# setwd(path)
# kableExtra::save_kable(table8, file='f_c_subsidy.png', zoom = 1.5)
