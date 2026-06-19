# Research Notes

This project treats lotto recommendations as statistical summaries, not reliable winning predictions.

## Sources Reviewed

- Coronel-Brizio et al., "Statistical auditing and randomness test of lotto k/N-type games", arXiv:0806.4595: https://arxiv.org/abs/0806.4595. The paper models lotto k/N games as random draws without replacement and uses hypergeometric/order-statistic expectations for auditing historical results.
- Kevin He, "Mislearning from Censored Data: The Gambler's Fallacy and Other Correlational Mistakes in Optimal-Stopping Problems", arXiv:1803.08170 / Theoretical Economics 2022: https://arxiv.org/abs/1803.08170. The paper discusses how people can misread random sequences through gambler's-fallacy reasoning.
- General combinatorics formula for lottery matching: for 6 numbers from 45, the jackpot probability is 1 / C(45, 6) = 1 / 8,145,060.

## Design Implications

- Do not claim that historical frequency predicts the next draw.
- Use historical data for transparent summaries: frequency, overdue count, repeated pairs, odd/even balance, low/high balance, and total-sum range.
- Present recommendations as "analysis-based candidates" with the method and warning visible.
- Keep the dashboard free and static so it can be shared through GitHub Pages.

## Current Recommendation Method

1. Load all stored Lotto 6/45 draws.
2. Score candidate combinations by:
   - historical frequency component,
   - overdue component,
   - odd/even balance,
   - low/high balance,
   - total sum range,
   - number bucket diversity,
   - limited consecutive pairs.
3. Remove combinations that exactly match a previous winning draw.
4. Publish the top 10 ranked combinations.

## Known Limit

This method can make recommendations look organized, but it does not overcome the randomness of the lottery. It is useful as a transparent dashboard project, not as an investment or income system.

## Fetch Verification Note

The default endpoint is `https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}`. In the local Codex environment on 2026-06-19, network access worked after approval, but the endpoint returned HTML instead of JSON. The code now fails loudly on non-JSON responses instead of silently producing bad data. Re-test this endpoint in the actual GitHub Actions environment after publishing.
