def calc_max_score(responses, selection, point_distribution, test_structure, variants_is_used):
    max_score = 0
    last_parent_id = None
    for item_id, store_item in responses.items.items():
        current_obj = test_structure.get_object(item_id)
        merged_responses = store_item.get_merged_responses(None)
        if current_obj.parent_id is not None and current_obj.parent_id == last_parent_id:
            continue
        last_parent_id = current_obj.parent_id
        if item_id== "task_variant_assignment":
            continue
        for response in merged_responses:
            if response.points is not None:
                max_score += float(response.points)
            else:
                if current_obj.point_distribution["gap"] is not None:
                    max_score += float(current_obj.point_distribution["gap"])
                else:
                    max_score += float(point_distribution["gap"])

    for item_id, store_item in selection.items.items():
        current_obj = test_structure.get_object(item_id)
        if current_obj.point_distribution["selection"] is not None:
            max_score += float(current_obj.point_distribution["selection"])
        else:
            max_score += float(point_distribution["selection"])
    if variants_is_used:
        max_score += 1
    return max_score
