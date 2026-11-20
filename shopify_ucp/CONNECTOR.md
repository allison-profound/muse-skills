# UCP

- UCP checks out [Meta Catalog](/opt/hatch/connectors/meta_catalog_search/CONNECTOR.md) products, or a storefront cart privately retained by the browser checkout handoff, with the merchant, paid with [Link by Stripe](/opt/hatch/connectors/stripe-link/CONNECTOR.md) or [Shop Pay](/opt/hatch/connectors/shop-pay/CONNECTOR.md). Run `/opt/hatch/bin/ucp-cli`. It needs no merchant sign-in.

- Read the [checkout protocol](references/checkout-protocol.md) before creating or completing a checkout, or checking an order placed through native checkout. The Shopping skill covers choosing and comparing products.

- A store whose own catalog a browser task read can be checked out directly by that task's `browser_task_id`; the checkout protocol says how. The CLI takes a store only to pick one of the stores that task read.

## Commands

- Every command except `order get` reads a JSON input file with snake_case keys. Omit unknown optional fields and empty strings. Output is JSON, and `--timeout-secs` changes the 30-second default.

```text
/opt/hatch/bin/ucp-cli cart create|get|update|cancel --input-file <file.json>
/opt/hatch/bin/ucp-cli checkout create|get|update|complete|cancel --input-file <file.json>
/opt/hatch/bin/ucp-cli order get --checkout-id <checkout_id>
```

- `cart` keeps an optional saved basket. `checkout create` makes a quote, `checkout update` changes buyer contact and shipping details, the delivery option or discount codes and `checkout complete` pays and places the order.

- `checkout get` and `order get` read the current state of a checkout or placed order. `checkout cancel` takes `{"checkout_id": "<checkout_id>"}` and ends a checkout that is not completed. A placed order is changed or cancelled with the merchant.

## Safety rules

- Creating a checkout moves no money. `checkout complete` requests the wallet approval and places the order, so run it in the foreground, never poll it, and run it again on the same checkout only in these cases: its output shows that payment did not start and says what to correct or when to run again, such as `error_code: payment_method_required`; its `error_code` is `link_requires_action` and the user has finished the Link step; `next_action` is `pay_again` and the user has chosen how to pay or agreed to try again; the user asks again after a denied or unanswered approval; or a service restart interrupted the run and the user has since agreed to run it again, as the next two rules describe. Never create a Link spend request yourself, because `checkout complete` creates the only one.

- A service restart can end `checkout complete` before it finishes. Its result, or a later notice that a background command needs recovery, then says the service or runtime restarted and carries no final CLI output. Run `order get` for that checkout and follow its `next_action`. When it shows no order and `next_action` is `pay_again`, tell the user the payment was interrupted before it finished, and ask whether to run it again. Ask this every time, for Link and for Shop Pay, including when that run would pay with no new approval. The restart hides whether they approved or denied a payment approval that was waiting, so do not run `checkout complete` again until they answer.

- When the user agrees, write the same completion input again and run `checkout complete`, without `checkout get` or `checkout update` first. That run asks for the wallet approval again unless an earlier approval already covers the payment, so do not promise the user another approval. If it stops with an error, follow that output. If a restart interrupts that run too, start again from `order get` and ask again, because an earlier yes does not cover a later run.

- A denied approval is the user's decision. Stop without placing the order, and wait for a new explicit request before trying again.

- Never copy the merchant, item, total, buyer, delivery or legal-link data the endpoint returns into a later input. The CLI keeps those authoritative values itself.

- `checkout cancel` runs without its own approval prompt, so run it only when the user asks to cancel that checkout. A denied or unanswered approval, `next_action: pay_again`, an interrupted payment or a move to the browser is not such a request.

- Keep raw result JSON, internal IDs, buyer contact details and shipping addresses out of replies.

## Related skills

- [Shopping](/opt/muse/skills/shopping/SKILL.md)

- Use `muse.skill_search` to find other skills and `muse.connector_search` to find other connectors.
