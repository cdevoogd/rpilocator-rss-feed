IMAGE_TAG = cdevoogd/rpilocator-ntfy
SAVE_LOCATION = /tmp/rpilocator-ntfy.docker
.PHONY: image
image:
	docker build --file="./build/Dockerfile" --tag="${IMAGE_TAG}" --rm .

.PHONY: save
save:
	docker save "${IMAGE_TAG}" -o "${SAVE_LOCATION}"
	@echo The exported docker image is available at '${SAVE_LOCATION}'
