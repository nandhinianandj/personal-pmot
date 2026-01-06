import {
  Button,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Input,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"

import { AnchorsService, AnchorCreate } from "../../client"

interface AddAnchorProps {
  isOpen: boolean
  onClose: () => void
  pmotId: string
}

const AddAnchor = ({ isOpen, onClose, pmotId }: AddAnchorProps) => {
  const queryClient = useQueryClient()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<AnchorCreate>()

  const mutation = useMutation({
    mutationFn: (data: AnchorCreate) =>
      AnchorsService.createAnchor({ pmotId, requestBody: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["anchors"] })
      onClose()
    },
  })

  const onSubmit = (data: AnchorCreate) => {
    mutation.mutate(data)
    reset()
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Add Anchor</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <form onSubmit={handleSubmit(onSubmit)}>
            <FormControl isInvalid={!!errors.content}>
              <FormLabel htmlFor="content">Content</FormLabel>
              <Input
                id="content"
                {...register("content", {
                  required: "Content is required",
                })}
              />
              <FormErrorMessage>
                {errors.content && errors.content.message}
              </FormErrorMessage>
            </FormControl>
          </form>
        </ModalBody>
        <ModalFooter>
          <Button
            colorScheme="blue"
            mr={3}
            onClick={handleSubmit(onSubmit)}
            isLoading={isSubmitting}
          >
            Save
          </Button>
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

export default AddAnchor
